import machine
from machine import I2C, Pin
import time
from lcd import I2cLcd

# Reparei que é obrigatório para passar no Github Actions
print("Teste")

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

# Configurações de Keypad
pinos_linhas = [13, 12, 14, 27]
pinos_colunas = [26, 25, 33]
linhas = [machine.Pin(p, machine.Pin.OUT) for p in pinos_linhas]
colunas = [machine.Pin(p, machine.Pin.IN, machine.Pin.PULL_DOWN) for p in pinos_colunas]

teclas = [
    ['1', '2', '3'],
    ['4', '5', '6'],
    ['7', '8', '9'],
    ['X', '0', '>']
]

# Função para leitura do Keypad
def ler_teclado():
    for i, linha in enumerate(linhas):
        linha.value(1) 
        for j, coluna in enumerate(colunas):
            if coluna.value() == 1: 
                linha.value(0)
                return teclas[i][j]
        linha.value(0)
    return None

# Função para atualização do LCD
def atualizar_lcd(linha1, linha2=""):
    lcd.clear()
    lcd.putstr(f"{linha1}\n{linha2}")

# Função para contagem no display LCD
def counter_converter(time):

    minutes = time //60
    seconds = time % 60
    return f"{minutes:02d}:{seconds:02d}"

def second_converter(time):
    seconds = time % 100
    seconds += (time // 100)*60

    return seconds


# Estados do Microondas
S_AGUARDANDO = 0
S_CONFIGURANDO = 1
S_RODANDO = 2
S_FINALIZADO = 3
S_PAUSADO = 4

estado_atual = S_AGUARDANDO
tempo_restante = 0
pausado = False

# Variáveis para temporização
ultimo_tick_teclado = time.ticks_ms()
ultimo_tick_relogio = time.ticks_ms()
ultimo_tick_buzzer = time.ticks_ms()

# Controles auxiliares do buzzer
contagem_apitos = 0
estado_buzzer = 0

print("\nMicro-ondas Iniciado")
atualizar_lcd("Micro-ondas", "Pronto!")

while True:
    # Leitura do Teclado
    tecla = None
    if time.ticks_diff(time.ticks_ms(), ultimo_tick_teclado) > 200: # Debounce
        tecla_lida = ler_teclado()
        if tecla_lida:
            tecla = tecla_lida
            ultimo_tick_teclado = time.ticks_ms()
    
    # Máquina de Estados
    if estado_atual == S_AGUARDANDO:
        if tecla and tecla.isdigit():
            estado_atual = S_CONFIGURANDO
            tempo_restante = int(tecla)
            atualizar_lcd("Tempo:", f"{(tempo_restante//100):02d}:{(tempo_restante%100):02d}")
            
    elif estado_atual == S_CONFIGURANDO:
        if tecla:
            if tecla.isdigit():
                # Limite de 4 dígitos
                if tempo_restante < 1000:
                    tempo_restante = (tempo_restante * 10) + int(tecla)
                    atualizar_lcd("Tempo:", f"{(tempo_restante//100):02d}:{(tempo_restante%100):02d}")
            elif tecla == '>': # Iniciar
                if tempo_restante > 0:
                    estado_atual = S_RODANDO
                    rele_magnetron.value(1) # Liga o relé/LED
                    ultimo_tick_relogio = time.ticks_ms() # Salva o tempo de início
                    atualizar_lcd("Aquecendo...", f"Tempo: {(tempo_restante//100):02d}:{(tempo_restante%100):02d}")
                    tempo_restante = second_converter(tempo_restante)
            elif tecla == 'X': # Cancelar
                estado_atual = S_AGUARDANDO
                tempo_restante = 0
                atualizar_lcd("Cancelado", "Pronto!")
            
    elif estado_atual == S_RODANDO:
        # Cronômetro
        if not pausado and time.ticks_diff(time.ticks_ms(), ultimo_tick_relogio) >= 1000:
            if tempo_restante <= 0:
                rele_magnetron.value(0) # Desliga o relé
                estado_atual = S_FINALIZADO
                contagem_apitos = 0
                ultimo_tick_buzzer = time.ticks_ms()
                atualizar_lcd("Finalizado!", "Pode retirar")
            else: 
                print(f"{tempo_restante}s")
                tempo_restante -= 1
                ultimo_tick_relogio = time.ticks_ms() # Reseta o timer para o próximo segundo
                atualizar_lcd("Aquecendo...", f"Tempo: {counter_converter(tempo_restante)}")
            
            

        # Botão de cancelar
        if tecla == 'X':
            pausado = True
            rele_magnetron.value(0)
            atualizar_lcd("Pausado", f"Tempo: {counter_converter(tempo_restante)}")
            estado_atual = S_PAUSADO

    elif estado_atual == S_PAUSADO:
        if tecla == '>':
            pausado = False
            estado_atual = S_RODANDO
        elif tecla == 'X':
            pausado = False
            atualizar_lcd("Cancelado", "Pronto!")
            estado_atual = S_AGUARDANDO
            tempo_restante = 0

    elif estado_atual == S_FINALIZADO:
        # Apita 3 vezes (3 ligadas + 3 desligadas = 6 transições)
        if contagem_apitos < 6:
            if time.ticks_diff(time.ticks_ms(), ultimo_tick_buzzer) > 2000: # A cada 10s
                estado_buzzer = not estado_buzzer
                buzzer.value(estado_buzzer)
                contagem_apitos += 1
                ultimo_tick_buzzer = time.ticks_ms()
        else:
            buzzer.value(0)
            estado_atual = S_AGUARDANDO
            
            
    # Sleep para o processamento do simulador Wokwi 
    time.sleep_ms(10)