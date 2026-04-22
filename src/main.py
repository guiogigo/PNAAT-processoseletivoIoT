import machine
from machine import I2C, Pin
import time
from lcd import I2cLcd

# Configurações de Hardware
buzzer = machine.Pin(15, machine.Pin.OUT)
rele_magnetron = machine.Pin(4, machine.Pin.OUT) # Controla o seu LED vermelho

# Configurações do LCD
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
lcd = I2cLcd(i2c, 0x27, 2, 16) # Inicia o Display
lcd.backlight_on() # Acende a luz


# Definições iniciais
buzzer.value(0)
rele_magnetron.value(0)
lcd.putstr("00:00") 

# Configurações de Keypad
pinos_linhas = [13, 12, 14, 27]
pinos_colunas = [26, 25, 33, 32]
linhas = [machine.Pin(p, machine.Pin.OUT) for p in pinos_linhas]
colunas = [machine.Pin(p, machine.Pin.IN, machine.Pin.PULL_DOWN) for p in pinos_colunas]

teclas = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'],
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D']
]


def ler_teclado():
    """Função para leitura do Keypad"""
    for i, linha in enumerate(linhas):
        linha.value(1) 
        for j, coluna in enumerate(colunas):
            if coluna.value() == 1: 
                linha.value(0)
                return teclas[i][j]
        linha.value(0)
    return None

# Estados do Microondas
S_AGUARDANDO = 0
S_CONFIGURANDO = 1
S_RODANDO = 2
S_FINALIZADO = 3

estado_atual = S_AGUARDANDO
tempo_restante = 0

print("\nMicro-ondas Iniciado")
print("Estado Atual: AGUARDANDO (Pressione qualquer número para configurar o tempo)")

while True:
    tecla = ler_teclado()
    
    if estado_atual == S_AGUARDANDO:
        if tecla and tecla.isdigit():
            estado_atual = S_CONFIGURANDO
            tempo_restante = int(tecla)
            print(f"\nEstado Atual: CONFIGURANDO - Tempo: {tempo_restante}s")
            print("Pressione números para adicionar, '#' para INICIAR ou 'D' para CANCELAR.")
            time.sleep(0.3) # Evita leitura dupla
            
    elif estado_atual == S_CONFIGURANDO:
        if tecla:
            if tecla.isdigit():
                # Adiciona dígitos 
                tempo_restante = (tempo_restante * 10) + int(tecla)
                print(f"Tempo ajustado: {tempo_restante}s")
            elif tecla == '#': # Iniciar
                estado_atual = S_RODANDO
                print("\nEstado Atual: RANDO (Relé ligado)")
            elif tecla == 'D': # Cancelar
                estado_atual = S_AGUARDANDO
                tempo_restante = 0
                print("\nOperação Cancelada. Estado Atual: AGUARDANDO")
            time.sleep(0.3) # Evita leitura dupla
            
    elif estado_atual == S_RODANDO:
        rele_magnetron.value(1) # Fecha o relé, acende o LED
        print(f"Tempo restante: {tempo_restante}s")
        time.sleep(1)
        tempo_restante -= 1
        
        if tempo_restante <= 0:
            rele_magnetron.value(0) # Abre o relé, apaga o LED
            estado_atual = S_FINALIZADO
            print("\nEstado Atual: FINALIZADO")
            
    elif estado_atual == S_FINALIZADO:
        # Apita o buzzer 3 vezes
        for _ in range(3):
            buzzer.value(1)
            time.sleep(0.3)
            buzzer.value(0)
            time.sleep(0.3)
        
        estado_atual = S_AGUARDANDO
        print("\nEstado Atual: AGUARDANDO (Pronto para nova operação)")
        
    time.sleep(0.05) # Sleep para não travar a simulação