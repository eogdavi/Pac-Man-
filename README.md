# Pac-Man- # 🟡 Pac-Man em Python

Jogo estilo Pac-Man feito com **Python** e **pygame**: labirinto, pontos, pílulas de poder, 4 fantasmas com comportamentos diferentes, vidas, recorde e túnel lateral.

## Como rodar

```bash
git clone https://github.com/SEU-USUARIO/pacman-python.git
cd pacman-python
pip install -r requirements.txt
python pacman.py
```

## Controles

| Tecla | Ação |
|-------|------|
| ← ↑ → ↓ ou WASD | Mover |
| ENTER | Reiniciar (fim de jogo / vitória) |
| ESC | Sair |

## Regras

- Ponto: 10 pts | Pílula de poder: 50 pts
- Com a pílula, os fantasmas ficam azuis e podem ser comidos (200, 400, 800, 1600 pts)
- Fantasma comido volta para a casa e reaparece
- 3 vidas. Coma todos os pontos para vencer

## Fantasmas

- 🔴 **Blinky** persegue você direto
- 🩷 **Pinky** tenta emboscar à sua frente
- 🩵 **Inky** combina sua posição com a do Blinky
- 🟠 **Clyde** persegue de longe e foge quando está perto

## Ideias para evoluir

- Sons e efeitos
- Várias fases com velocidade crescente
- Frutas bônus
- Salvar o recorde em arquivo

## Licença

MIT
