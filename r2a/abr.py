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
      self.container = [0] * 20
      self.bestq = 0

    def add_container(self, element):
        i = 0 # indice
        bestt = element[0]/element[1] #throuput
        #print("analisando qualidade para throuput:", element)
        for x in self.qi: #aproxima o throuput em relaçao as qualidades
            if x > bestt: #testa o maior throuput em relacao a entrada
                #print("qualidade selecionada :", i)
                self.container[i] = element[1] #se sim salva no container o tempo de requisicao
                break
            i+=1 #incrementa o index

        bestval = 10000000000000
        i = 0

        for x in self.container: #escolhe o melhor tempo salvo no container
            if x <= bestval:
                self.bestq = i #marca o indice com o melhor tempo
                bestval = x
            i+=1

        amount_rest = self.whiteboard.get_amount_video_to_play() #usa o amount rest e o playback_qi como metrica de comparacao
        playback_qi = self.whiteboard.get_playback_qi()

        if playback_qi:
            difval = playback_qi[-1][0] - playback_qi[-2][0] #pega os ultimos valores da lista dos ultimos tempos de video tocados e compara
            compare = self.bestq
            if difval > 1.9 or amount_rest > 50: #se a diferenca for maior que 1.9 o algoritmo prioriza o desempenho
                self.bestq = 5
            elif difval < 1.5: #se a diferenca for menor que 1.5 o algoritmo prioriza a qualidade do video
                self.bestq = random.randint(6, compare)

    def get_container(self): #retorna o index de melhor qualidade
        return self.bestq

    def handle_xml_request(self, msg): #calcula os tempos de request
        self.request_time = time.perf_counter()
        self.send_down(msg)

    def handle_xml_response(self, msg):
        parsed_mpd = parse_mpd(msg.get_payload()) #pega a lista de qualidades disponiveis de video
        self.qi = parsed_mpd.get_qi()
        
        t = time.perf_counter() - self.request_time
        self.add_container((msg.get_bit_length(), t)) #Salva no container os dados a serem mensurados
    
        self.send_up(msg)

    def handle_segment_size_request(self, msg):
        self.request_time = time.perf_counter() #calcula o tempo de requisiçao

        #print(self.whiteboard)
        #print(self.container)
        
        bestval = self.get_container() #pega do container a melhor qualidade
        selected_qi = self.qi[bestval] #seleciona a qualidade
        msg.add_quality_id(selected_qi)
        self.send_down(msg)

    def handle_segment_size_response(self, msg):
        t = time.perf_counter() - self.request_time
        self.add_container((msg.get_bit_length(), t)) #Salva no container os dados a serem mensurados
        self.send_up(msg)

    def initialize(self):
        pass

    def finalization(self):
        pass
