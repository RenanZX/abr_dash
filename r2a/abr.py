import time
from player.parser import *
from r2a.ir2a import IR2A
from statistics import mean
import random

class ABR(IR2A):
    def __init__(self, id): #inicializa as variaveis
      IR2A.__init__(self,id)
      self.request_time = 0
      self.qi = []
      self.tempos = [0] * 20
      self.bestperf = 0
      self.besttime = 10000000000000

    def set_tempos(self, element):
        bestt = element[0]/element[1] #throuput
        #print("analisando qualidade para throuput:", element)
        mid = int(len(self.qi)/2)
        maxv = len(self.qi) - 1
        minv = 0

        if bestt >= self.qi[mid]:
            rang = range(mid+1, maxv)
        elif bestt < self.qi[mid]:
            rang = range(minv, mid)

        for i in rang: #aproxima o throuput em relaçao as qualidades
            if self.qi[i] > bestt: #testa o maior throuput em relacao a entrada
                #print("qualidade selecionada :", i)
                self.tempos[i] = element[1] #se sim salva na lista de tempos o tempo de requisicao
                break

        mid = int(len(self.tempos)/2) + 4
        maxv = len(self.tempos) - 1
        minv = 9

        if self.besttime > self.tempos[mid]:
            rang = range(mid+1, maxv)
        elif self.besttime <= self.tempos[mid]:
            rang = range(minv, mid)
        
        for i in rang: #escolhe o melhor tempo salvo na lista de tempos
            if self.tempos[i] <= self.besttime:
                self.bestperf = i #marca o indice com a melhor performance
                self.besttime = self.tempos[i]

        amount_rest = self.whiteboard.get_amount_video_to_play() #usa o amount rest e o playback_qi como metrica de comparacao
        playback_qi = self.whiteboard.get_playback_qi()
        buf = self.whiteboard.get_buffer() #buffer do whriteboard
        maxbuf = self.whiteboard.get_max_buffer_size() #tamanho maximo do buffer, caso o buffer esteja cheio sera priorizado a performance
        pbpause = len(self.whiteboard.get_playback_pauses())

        if len(playback_qi) > 1:
            difval = playback_qi[-1][0] - playback_qi[-2][0] #pega os ultimos valores da lista dos ultimos tempos de video tocados e compara
            compare = self.bestperf
            if difval > 1.9 or amount_rest > 50 or len(buf) > maxbuf: #se a diferenca for maior que 1.9 o algoritmo prioriza o desempenho
                self.bestperf = 5
            elif difval < 1.5: #se a diferenca for menor que 1.5 o algoritmo prioriza a qualidade do video
                self.bestperf = random.randint(10, 15)
            if pbpause > 2 and pbpause < self.bestperf:
               self.bestperf-=pbpause

    def get_best_time(self): #retorna o index de melhor qualidade
        return self.bestperf

    def handle_xml_request(self, msg): #calcula os tempos de request
        self.request_time = time.perf_counter()
        self.send_down(msg)

    def handle_xml_response(self, msg):
        parsed_mpd = parse_mpd(msg.get_payload()) #pega a lista de qualidades disponiveis de video
        self.qi = parsed_mpd.get_qi()
        
        t = time.perf_counter() - self.request_time
        self.set_tempos((msg.get_bit_length(), t)) #Salva na lista de tempos os dados a serem mensurados
    
        self.send_up(msg)

    def handle_segment_size_request(self, msg):
        self.request_time = time.perf_counter() #calcula o tempo de requisiçao

        print(self.whiteboard)
        #print(self.container)
        
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
