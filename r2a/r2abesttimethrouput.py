import time
from player.parser import *
from r2a.ir2a import IR2A
from statistics import mean
import random
import math

class R2ABestTimeThrouput(IR2A):
    def __init__(self, id): #inicializa as variaveis
      IR2A.__init__(self,id)
      self.request_time = 0
      self.qi = []
      self.tempos = []
      self.bestperf = 0
      self.besttime = 10000000000000
      self.lastpause = -1

    def set_tempos(self, element):
        throuput = element[0]/element[1] #throuput
        high = len(self.qi) - 1
        low = 0
        weight = 0.8 #peso inicial
        qualityid = len(self.qi)

        while low <= high: #aproxima o throuput em relaçao as qualidades utilizando busca binaria
            mid = (high + low)//2

            if throuput < self.qi[mid]: 
                low = mid + 1

            elif throuput > self.qi[mid]: 
                high = mid - 1
            
            if self.qi[mid] > throuput: #testa o maior throuput em relacao a entrada
                self.tempos[mid] = element[1] #se sim salva na lista de tempos o tempo de requisicao
                if mid > weight and element[1] < self.besttime: #checa se a qualidade encontrada e boa e faz o repeso dependendo do tempo de requisicao
                    weight = mid//len(self.qi)
                break

        amount_rest = self.whiteboard.get_amount_video_to_play() #usa o amount rest e o playback_qi como metrica de comparacao
        playback_qi = self.whiteboard.get_playback_qi()
        buf = self.whiteboard.get_buffer() #buffer do whriteboard
        maxbuf = self.whiteboard.get_max_buffer_size() #tamanho maximo do buffer, caso o buffer esteja cheio sera priorizado a performance
        pbpause = self.whiteboard.get_playback_pauses()

        if element[1] > self.besttime: # a pesagem é nivelada de acordo com o throuput recebido como parametro
            weight -= 0.2
        elif element[1] < self.besttime:
            weight += 0.2

        if len(playback_qi) > 1:
            difval = playback_qi[-1][0] - playback_qi[-2][0] #pega os ultimos valores da lista dos ultimos tempos de video tocados e compara
            if difval > 1.9 or amount_rest > 50: #se a diferenca for maior que 1.9 o algoritmo prioriza o desempenho
                weight -= 0.2
            elif difval < 1.5: #se a diferenca for menor que 1.5 o algoritmo prioriza a qualidade do video
                weight += 0.2
            
            if difval <= 1.1:
                weight += 0.001

            if len(buf) > maxbuf: #se o buffer tiver muito cheio, prioriza o desempenho
                weight =  0.2
            
            if len(pbpause) > 0 and self.lastpause != pbpause[-1][1]:
                self.lastpause = pbpause[-1][1] #pega o tempo do ultimo pause ocorrido
                if self.lastpause > 20 or len(pbpause) > 2: #repesa caso hajam interrupções da transmissao
                    weight = 0.2

        if weight > 1: #nivela o intervalo dos pesos
            weight = 0.7
        elif weight < 0:
            weight = 0.2
            
        self.besttime = self.tempos[int(weight*qualityid)] #escolhe o melhor peso e salva
        self.bestperf = int(weight*qualityid)

    def get_best_time(self): #retorna o index de melhor qualidade
        return self.bestperf

    def handle_xml_request(self, msg): #calcula os tempos de request
        self.request_time = time.perf_counter()
        self.send_down(msg)

    def handle_xml_response(self, msg):
        parsed_mpd = parse_mpd(msg.get_payload()) #pega a lista de qualidades disponiveis de video
        self.qi = parsed_mpd.get_qi()
        self.tempos = [0] * len(self.qi)
        
        t = time.perf_counter() - self.request_time
        self.set_tempos((msg.get_bit_length(), t)) #Salva na lista de tempos os dados a serem mensurados
    
        self.send_up(msg)

    def handle_segment_size_request(self, msg):
        self.request_time = time.perf_counter() #calcula o tempo de requisiçao

        bestval = self.get_best_time() #pega da lista a melhor qualidade
        selected_qi = self.qi[bestval] #seleciona a qualidade
        msg.add_quality_id(selected_qi)
        self.send_down(msg)

    def handle_segment_size_response(self, msg):
        t = time.perf_counter() - self.request_time
        self.set_tempos((msg.get_bit_length(), t)) #Salva na lista de tempos os dados a serem mensurados
        self.send_up(msg)

    def initialize(self):
        pass

    def finalization(self):
        pass
