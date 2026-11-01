# Enigma Lab — Frontend inicial

Protótipo de interface em HTML, CSS e JavaScript puro para o projeto educativo da máquina Enigma.

## Estrutura
- `index.html`: nove telas e navegação.
- `css/style.css`: identidade visual responsiva.
- `js/app.js`: navegação e interações demonstrativas.
- `assets/images/`: reservado para futuras imagens.

## Executar
1. Extraia a pasta `frontend` para dentro da pasta do projeto Enigma.
2. Abra `index.html` no navegador ou use a extensão Live Server no VS Code.
3. Navegue pelas nove telas pelo menu lateral.

Não há dependências de JavaScript para instalar. As fontes externas usam Google Fonts; o sistema mantém fontes de reserva caso não haja internet.

## Limitações
- A cifragem e descriptografia da tela Máquina são transformações fictícias para demonstrar a interface, **não são a cifra Enigma real**.
- O percurso da letra e os resultados de criptoanálise são ilustrativos.
- Os desafios são demonstrativos e não devem ser tratados como mensagens históricas autenticadas.
- O progresso fica apenas em memória durante a sessão e será reiniciado ao recarregar.
- O backend Python ainda não está conectado.

## Próxima etapa
Integrar a interface ao motor Python existente por uma API, sem duplicar a lógica criptográfica em JavaScript. Compare esta pasta com a estrutura real do projeto antes de mover ou substituir arquivos Python.


## Revisão visual
O dashboard foi reorganizado com paleta escura, cartões coloridos, ilustração SVG da Enigma e regras responsivas para desktop, tablet e celular. A lógica criptográfica continua demonstrativa até a integração com o backend Python.
