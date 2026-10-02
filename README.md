# Check Point 2 – ESP32 + MicroPython + LCD I2C + API OpenWeather + MQTT/Node-RED

**Alunos:** Filipe Scal de Araujo, Gabriel de Medeiros Madureira, Luis Gustavo Leonart Evangelista, Francisco Antonio Garcia Saia 
**RMs:** 569175, 570297, 572167, 571541
**Turma:** 1EMA – Engenharia Mecatrônica 

## Descrição

Projeto simulado no **Wokwi** (executado dentro do Cursor) em que um **ESP32** programado em **MicroPython**:

1. Conecta na rede Wi-Fi do Wokwi (`Wokwi-GUEST`);
2. Consulta a **API OpenWeather** para obter o clima atual de São Paulo;
3. Exibe os dados em um **display LCD 20x4 (I2C)**;
4. **Publica** os mesmos dados em formato JSON em um broker **MQTT** público (HiveMQ);
5. Um fluxo no **Node-RED** assina o tópico e exibe as mensagens recebidas.

```
OpenWeather API ──HTTP──► ESP32 ──I2C──► LCD 20x4
                           │
                           └──MQTT──► broker.hivemq.com ──► Node-RED (mqtt in → debug)
```

## Estrutura dos arquivos

| Arquivo | Função |
|---|---|
| `main.py` | Programa principal: Wi-Fi, consulta à API, LCD e publicação MQTT |
| `lcd_api.py` | Biblioteca base para controle do LCD (HD44780) |
| `i2c_lcd.py` | Driver do LCD via I2C (PCF8574) |
| `diagram.json` | Circuito do Wokwi (ESP32 + LCD 20x4 I2C) |
| `wokwi.toml` | Configuração do Wokwi (firmware e porta RFC2217) |
| `firmware.bin` | Firmware MicroPython para ESP32 |

## Ligações do circuito

| LCD I2C | ESP32 |
|---|---|
| GND | GND |
| VCC | 3V3 |
| SDA | GPIO 21 |
| SCL | GPIO 22 |

Endereço I2C do LCD: `0x27`.

## Configuração

No início do `main.py`, ajuste:

```python
SSID = "Wokwi-GUEST"          # rede Wi-Fi do Wokwi (sem senha)
PASSWORD = ""
API_KEY = "SUA_CHAVE_AQUI"    # chave da OpenWeather
CIDADE = "Sao%20Paulo,BR"

BROKER = "broker.hivemq.com"
TOPICO = b"fiap/cp2/Filipe_Scal/clima"
```

> **Atenção:** não publique sua chave da OpenWeather em repositórios públicos. Mantenha `SUA_CHAVE_AQUI` no código enviado e use a chave real apenas localmente.

A chave é gratuita e pode ser criada em [openweathermap.org](https://openweathermap.org) (menu do perfil → *My API keys*). Chaves novas podem levar até algumas horas para ativar (erro 401 enquanto isso).

## Como executar

### 1. Pré-requisitos

- Cursor (ou VS Code) com a extensão **Wokwi Simulator**
- Python e o **mpremote**:
  ```
  pip install mpremote
  ```

### 2. Iniciar a simulação

Abra o `diagram.json` e inicie a simulação (*Wokwi: Start Simulator*). Mantenha-a rodando.

### 3. Enviar os arquivos para o ESP32

No Wokwi dentro do Cursor, o `main.py` não é carregado automaticamente no ESP32. Em outro terminal, na pasta do projeto, envie os arquivos com o mpremote:

```
python -m mpremote connect port:rfc2217://localhost:4000 fs cp lcd_api.py i2c_lcd.py main.py :
```

Para conferir se os arquivos chegaram:

```
python -m mpremote connect port:rfc2217://localhost:4000 fs ls
```

Reinicie o ESP32 na simulação. O LCD mostra "Conectando WiFi...", depois "Conectando MQTT..." e então os dados do clima.

> Ao parar e iniciar a simulação do zero, os arquivos somem do ESP32 e é preciso enviá-los de novo. Com um reset simples eles continuam lá.

### 4. Node-RED

1. Instale e inicie (requer Node.js):
   ```
   npm install -g node-red
   node-red
   ```
2. Abra `http://localhost:1880`.
3. Monte o fluxo **mqtt in → debug**:
   - Servidor: `broker.hivemq.com`, porta `1883`
   - Tópico: `fiap/cp2/Filipe_Scal/clima` (igual ao `TOPICO` do `main.py`)
   - QoS: `0`
4. Clique em **Implementar** e abra a aba de depuração.

As mensagens chegam como JSON, por exemplo:

```json
{"temp": 17.54, "cidade": "São Paulo", "vento": 4.63, "umidade": 81, "ceu": "Clouds"}
```

## Dados exibidos no LCD

```
São Paulo
Temp: 17.5 C
U:81% V:4.63m/s
Clouds
```

(O display não possui caracteres acentuados, por isso o "ã" pode aparecer diferente.)

## Evidências

> Inclua aqui os prints:
>
> 1. LCD no Wokwi mostrando os dados do clima
> 2. Node-RED com o nó `mqtt in` conectado e as mensagens na janela de depuração

## Problemas comuns

| Sintoma | Causa provável | Solução |
|---|---|---|
| LCD vazio | Arquivos não enviados ao ESP32 | Repetir o `fs cp` e reiniciar |
| `Erro na API – 401` | Chave inválida ou ainda não ativada | Conferir `API_KEY` e aguardar ativação |
| "Falha no WiFi" | Rede ou senha incorretas | Usar `Wokwi-GUEST` com senha vazia |
| "Falha no MQTT" | Broker indisponível | Tentar de novo ou usar `test.mosquitto.org` |
| `Failed to parse JSON string` no Node-RED | Mensagem de outro publicador no tópico | Usar a saída em auto-detecção e um tópico mais único |
| Nenhuma mensagem no Node-RED | Tópico diferente do `main.py` | Conferir letra por letra |
| `run main.py` trava o terminal | Programa em `while True` | Sair com `Ctrl+C` |

## Tecnologias

ESP32 · MicroPython · Wokwi · I2C · LCD 20x4 · OpenWeather API · MQTT (HiveMQ) · Node-RED
