# Anomalias de IDs — Matriz_Pessoas_SRC_Horizon_Egressos.xlsx

**Gerado em:** 2026-09-24  
**Total de IDs analisados:** 10.615  
**Total de IDs anômalos:** 239 (2,25%)  
**Fonte:** [Matriz_Pessoas_SRC_Horizon_Egressos.xlsx](file:///home/pedrolino7/Documentos/comparaListas/Matriz_Pessoas_SRC_Horizon_Egressos.xlsx)

---

## Resumo por Categoria

| Cod | Severidade | Problema | Qtd |
|---|---|---|---|
| A | 🔴 Crítico | Slug numérico — sem nome real | 2 |
| F | 🔴 Crítico | Slug gerado de ID Horizon sem nome válido | 1 |
| B | 🔴 Crítico | Palavra solta — não representa um nome de pessoa | 13 |
| CD | 🔴 Crítico | Dois nomes colados + título de projeto embutido | 8 |
| C | 🟠 Alto | Dois nomes de pessoas distintas colados num único ID | 191 |
| D | 🟠 Alto | Nome da pessoa + título de trabalho embutido | 8 |
| E | 🟡 Moderado | Abreviação bibliográfica — lista de autores comprimida | 16 |
| — | — | **Total** | **239** |

---

## A — Slug Numérico (sem nome real) · 2 casos

> [!CAUTION]
> O slug é apenas o ID numérico. O Horizon importou um registro sem campo nome preenchido e o pipeline usou o número como fallback. Esses IDs não representam nenhuma pessoa identificável.

| ID | Slug | Ação recomendada |
|---|---|---|
| 1 | `1` | Investigar no Horizon e descartar ou substituir pelo nome real |
| 2 | `2` | Investigar no Horizon e descartar ou substituir pelo nome real |

## F — ID Horizon Inválido · 1 caso

> [!CAUTION]
> O pipeline detectou que o nome no Horizon era inválido e gerou este slug de diagnóstico. Indica dado corrompido na fonte (person id=1921 no Horizon).

| ID | Slug | Ação recomendada |
|---|---|---|
| 4400 | `horizon-nome-invalido-id-1921` | Verificar person id=1921 no Horizon; corrigir na fonte ou descartar |

## B — Palavra Solta / Ruído de Importação · 13 casos

> [!CAUTION]
> O slug contém apenas uma única palavra sem separador kebab-case. Não é um nome completo de pessoa.

| ID | Slug | Tipo de problema |
|---|---|---|
| 35 | `adelia` | Primeiro nome apenas — sem sobrenome |
| 42 | `adikto` | Apelido/username — não é nome real |
| 1519 | `cabral` | Sobrenome isolado — altamente ambíguo |
| 2544 | `dr` | Título acadêmico capturado como nome |
| 4267 | `helder` | Primeiro nome apenas — sem sobrenome |
| 6143 | `licenciatura` | Modalidade de curso importada como nome de pessoa |
| 7589 | `me` | Abreviação "ME" capturada como nome |
| 8348 | `prof` | Título acadêmico capturado como nome |
| 8351 | `profa` | Título acadêmico capturado como nome |
| 8596 | `rathael` | Primeiro nome apenas — sem sobrenome |
| 8801 | `rhian` | Primeiro nome apenas (possivelmente estrangeiro) |
| 8975 | `rodrigo` | Primeiro nome isolado — altamente ambíguo |
| 10546 | `xxx` | Placeholder / valor nulo fictício |

## CD — Dois Nomes Colados + Título Embutido · 8 casos

> [!WARNING]
> Acúmulo dos problemas C e D: dois nomes de pessoas distintas colados num único ID **e** o título do trabalho também foi concatenado ao slug.

| ID | Slug (truncado) | Pessoa 1 | Pessoa 2 | Problema adicional |
|---|---|---|---|---|
| 1502 | `bruno-rocha-pratti-instrumentacao-de-um-drone-restaurador-florestal-de...` | Bruno Rocha Pratti Instrumentacao De Um Drone Restaurador Florestal De Tecnologia Lora Desenvolvimento De Um Algoritmo Para Navegacao De Um Drone Usando Sensores Inerciais | Dados De Gps Pt 9692 | Título: *—...* |
| 3058 | `ernandes-moises-ribeiro-de-souza-construcao-modelagem-e-controle-de-um...` | Ernandes Moises Ribeiro De Souza Construcao Modelagem | Controle De Um Aeroestabilizador | Título: *—...* |
| 3319 | `felipe-jose-pesca-orientacao-de-estagio-do-curso-de-engenharia-de-cont...` | Felipe Jose Pesca Orientacao De Estagio Do Curso De Engenharia De Controle | Automacao Na Controlmec Com Serv | Título: *—...* |
| 4205 | `gutto-gabriel-kuster-lube-e-mauricio-g-pinheiro-guerra-sistema-de-gest...` | Gutto Gabriel Kuster Lube | Mauricio G Pinheiro Guerra | Título: *sistema de gestao iso 14001 aplicado a reducao de ...* |
| 4674 | `izabella-campos-trarbach-controle-e-monitoramento-de-um-portao-de-gara...` | Izabella Campos Trarbach Controle | Monitoramento De Um Portao De Garagem Inteligente Baseado Em Internet Das Coisas Iot | Título: *desenvolvimento de um algoritmo de controle monito...* |
| 6680 | `luiza-broseghini-pin-desenvolvimento-de-um-sistema-de-monitoramento-re...` | Luiza Broseghini Pin Desenvolvimento De Um Sistema De Monitoramento Remoto Do Nivel De Um Rio | Alerta De Transbordamentos Para Populacoes Em Risco | Título: *desenvolvimento de um sistema de monitoramento rem...* |
| 6788 | `marcela-ribeiro-cabral-sistema-de-vigilancia-alimentar-e-nutricional...` | Marcela Ribeiro Cabral Sistema De Vigilancia Alimentar | Nutricional | Título: *—...* |
| 10270 | `vitor-de-sa-nunes-desenvolvimento-de-um-sistema-de-monitoramento-remot...` | Vitor De Sa Nunes Desenvolvimento De Um Sistema De Monitoramento Remoto Do Nivel De Um Rio | Alerta De Transbordamentos Para Populaco | Título: *—...* |

## C — Dois Nomes Colados num Único ID · 191 casos

> [!WARNING]
> O campo de nome na fonte original (Egressos ou orientações do Horizon) foi preenchido com dois nomes separados por " e ".  
> O pipeline gerou **um único ID para ambos**, tornando as duas pessoas invisíveis individualmente na integração.

| ID | Pessoa 1 (inferida) | Pessoa 2 (inferida) |
|---|---|---|
| 29 | Adam Santos Nascimento | Luedy Steime Lima Mendes |
| 36 | Adelson Cassioli | Carlos Arthur Pandolfi Lopes |
| 39 | Ademar Goncalves Das Candeias Junior | Paula Marabotte Sasso |
| 99 | Adrianne Nascimento De A Rodrigues | Marizete Barbosa Stein |
| 126 | Adson Gouveia Machado | Emmanoel C Da Silva Oliveira Neto |
| 181 | Albenir Rodrigues Junior | Thiago Arita Salcides |
| 201 | Aldo Henrique Santos De Matos | Patrick Alves Cardoso |
| 230 | Alessandra Lignani De Miranda Starling | Albuquerque |
| 293 | Alexandre Ferreira Viana | Filipe De Castro Ferreira |
| 306 | Alexandre Mello De Carvalho | Ramiro Ceolin Lirio |
| 323 | Alexandro A Da Silva Junior | Gilmar S Santana Filho |
| 333 | Alexsander Xisto Moreira | Leandro Caetano Bonjardim |
| 392 | Aline Gues Fernandes | Tessy Yoshana Okuma |
| 435 | Almir Carlos Costa Da Silva | Gabriela De Souza Simoes |
| 459 | Alvaro Pedro Diodino Junior | Thiago Fairich Carvalho |
| 506 | Amanda Franco Martins | Maria Clara Pereira Santos |
| 518 | Amanda Menegussi | Luciana Aparecida Selia De Castro |
| 528 | Amanda Pereira Costa Brandao | Mariele W Klippel |
| 537 | Amanda Simoes De Assis | Filipe Benevides Mendonca |
| 589 | Ana Carolina Mariath Magalhaes Correa | Castro |
| 734 | Anderson Alves Da Silva | Weverton Bruno Ramos Dos Santos |
| 739 | Anderson Breda | Samanta Dias De Oliveira |
| 755 | Anderson Pelissari Vieira | Renato De Moura Santos |
| 785 | Andre Conceiro Bastos | Fernanda Braz Pinto |
| 816 | Andre Luiz Bimbato De Moraes | Charles Stefenoni Queiroz |
| 822 | Andre Luiz R Silva | Samir Soares Lima |
| 884 | Andressa Bastos Ferrari | Luana De Andrade Oliveira |
| 895 | Andressa Nunes De Oliveira | Cassia Lucas Moet |
| 971 | Anny Isabelle Oliveira Andrade | Maria Eduarda Freitas Silva |
| 974 | Anselmo Frizera Neto | Dinesh Kant Kumar |
| 977 | Anthony Bravin Costa | Rosiane Da Silva Sangali |
| 982 | Antonio A Freire De Lima Junior | Ramon Santos Mendonca |
| 984 | Antonio C Marinho | Gama I Pamplona R Bins S |
| 1067 | Arlene Brandao Sousa Martins | Louase Dos Santos Castilho |
| 1225 | Barbara Zamprogno | Eliezer Soares De Souza |
| 1320 | Bobby Hary Lima | Messias Pereira Da Silva Junior |
| 1349 | Brenno Augusto Duarte Claves | Danielle Calazans Dondoni |
| 1370 | Breno Schneider Nascimento | Welida Diniz Rodrigues |
| 1421 | Brunela Mauro Bermudes Campos | Bruno Gambiarti |
| 1428 | Bruno Aguiar Soares | Herculina Alencar Silva |
| 1485 | Bruno Mendes Medeiros | Luiz C Lozer |
| 1505 | Bruno S Rangel Heitor A Coelho | Rafael Z Fernandes |
| 1558 | Caio Teixeira Do Espirito Santo | Wesley Victor Carcheno |
| 1598 | Camila Soares Nascimento | Ringley Ferreira Bueno Braga |
| 1608 | Camilo Zucchetto Nippes | Daniel Bussular Diniz |
| 1621 | Carla Dias Do Nascimento Souza | Rosangela De Souza Venturin |
| 1625 | Carla Pereira Jardim | Luiz Gustavo Pereira Dos Santos |
| 1635 | Carlinda Alves Caetano | Stephanie Rhanna De Oliveira Silva |
| 1640 | Carlos Alberto Da Rocha Filho | Jhenifer Correa Peixoto |
| 1645 | Carlos Alberto Recla Junior | William Fiorotti Cordeiro |
| 1663 | Carlos De M Netto Murilo Rezende | Nivea C P Degasperi |
| 1665 | Carlos | Laquine Felipe M Barros Fabricio C De Araujo |
| 1691 | Carlos Gomide | Erika Maria Dos Santos Mafra Batista Vaz |
| 1694 | Carlos Henrique Arreco | Sirlene Dos Santos Oliveira |
| 1708 | Carlos Jose Bulado | Renato De Lima Junior |
| 1748 | Carolina Giovana Patrocinio | Renan Freitas Almeida |
| 1758 | Caroline Costa | Thiago Godinho Dos Santos |
| 1772 | Caroline Zatta De Moraes | Keith Harrison Sperandio |
| 1870 | Chrysthian Moizes | Davy Goncalves Cardoso Lima |
| 1918 | Claudia Cristina Nardi | Ingrid Firme Guedes |
| 1950 | Claudio Cesar Araujo Coelho | Jose Henrique Da Cunha Azevedo |
| 1962 | Clauzembergue Borges Junior | Emilio Da Silva Nunes |
| 1986 | Cleiton M Martins Alves | Victor A De Abreu Pimenta |
| 2024 | Cristiane Da Penha Martins Francismaicom Del Puppo | Rosiva |
| 2055 | Custodia Da Costa Dalbem | Daniele Nunes Santana |
| 2076 | Dalmacia De Souza Contarato | Marcus Vinicius Da Rocha |
| 2109 | Daniel De Souza Correia | Vitor Rangel Roque |
| 2168 | Daniela Da Gama | Silva Volpe Moreira De Moraes |
| 2186 | Danieli Sabrina Cherubino Simoes | Luciana Caliman Candeias |
| 2293 | Dayane De Angeli Da Cunha | Nelma Martins De Oliveira |
| 2310 | Debora Braga Dos Santos S Cosme | Samylle De Sousa Lirio |
| 2348 | Deisy De Souza Silva | Jucilene Trindade Da Silva Dalmaso |
| 2355 | Dejaime Manoel Do Rosario Filho | Lorena Paiva Pereira Da Si |
| 2400 | Deuse Mery Albani | Alidiane Callente Natale |
| 2414 | Diana Pacheco | Maysa Ramos Neves Nunes |
| 2467 | Diego Thadeu Juvenato | Leonardo Tavares Vieira |
| 2538 | Douglas R Salaroli Kenia Uliana Fagundes | Luiz H Vieira |
| 2555 | Dyeneffer Brandao Vitorio | Alexandro Brandao Santana |
| 2564 | Ecleia Maria Da Silva | Joao Carlos Martinelli |
| 2585 | Edileuza De Jesus Souza | Katyucy Gabriel Ferreira Pessotti |
| 2587 | Ediliane Sales Constancio | Joelma Goncalves Pereira |
| 2708 | Eduardo Paneto Goncalves | Marina Baeta Espinola |
| 2725 | Eduardo Roque Anacleto | Fenix Collistet De Araujo Fichter |
| 2814 | Elidia Da Piedade Oliveira Paulo | Rosimar Tolentino Lucas |
| 2820 | Eliete Klein | Laudiceia Dos Santos Faustino |
| 2865 | Elizabete Gomes | Ruth Leia F Cima Dos Santos |
| 2946 | Emerson Bolsoni Teixeira | Renan Tresman Eleoterio |
| 3028 | Erick Lima Regiani | Heudes Vieira Cruz Junior |
| 3239 | Fabiola Goncalves Pavao | Patricia Dos Reis De Carvalho |
| 3275 | Fagna Galdino Moreira | Priscila Santos Vieira |
| 3281 | Fatima Kefler Da Silva | Rafraele Cristina Walger Lodi |
| 3323 | Felipe M De Oliveira Carvalho | Rafael Cavalcante Menezes |
| 3341 | Felipe Schirmann Francisco | Valber Francisco Falcheto |
| 3356 | Fellipe De Oliveira Barboza | Mariana Marizani Mateus |
| 3384 | Fernanda Gnocchi Batista | Geisa Amelia Lopes |
| 3420 | Fernando Cardoso Jardim | Hugo Henrique Correia Da Silva |
| 3454 | Filipe Eduardo Ferreira De Abreu | Geraldo Buzim Del Piero |
| 3510 | Flavia Ungarato Ferreira | Ana Paula Correa |
| 3563 | Francine Perovano Batista | Lorenna Rocha Rosa |
| 3739 | Gabriel Vantil Garioli | Vagner Luiz Campos |
| 3795 | Gabrielly Silva Lorencini | Mayara Campanharo Belo |
| 3803 | Galvao Rumao Gomes De Franca | Israel Victor Nunes Araujo |
| 3869 | Gesse De Paula | Paula Adrielle Stefanelli Lima |
| 3955 | Gisele Alves Pinheiro | Irgley Couto De Souza |
| 3979 | Giulia W Teixeira | Silva Mario F Da Silva Rodrigues |
| 3993 | Glauber Cassimiro Campos | Josias De Souza |
| 4027 | Graziella C Paneto Ricardo P Ventorin | Sidmara V Correa |
| 4073 | Guilherme Farina Pena | Keslley Christian Rosario |
| 4076 | Guilherme G Queiroz Da Silva | Matheus Santana De Jesus |
| 4118 | Guilherme Vieira De Santana Silva | Tamires Rocha Cruz |
| 4127 | Gustavo B Pinto Leite | Marcelo Tavares Barboza |
| 4150 | Gustavo De Souza Cruz | Raphael De Souza Pereira |
| 4178 | Gustavo Neves Dias | Keitty De Souza Fernandes |
| 4265 | Helber Campos Lima | Mateus Oliveira Celestino |
| 4346 | Herbethy Bastos Barboza | Naiane Gomes Pesse |
| 4412 | Hueliton Pandolfi | Thiciano Da Ros Rosa |
| 4470 | Igildo Machado Soares | Sergio Rodrigues Silva |
| 4477 | Igor Chagas Silva | Isoneida Marini Brum |
| 4498 | Igor Soares Santos | Job Fontes De Oliveira Junior |
| 4506 | Ilson R Ferrerira Julio A Dos Anjos | Thiago B Sarcinelli |
| 4630 | Isoel C Carrasco Habisay D Dos Santos | Levy B Da Silva |
| 4767 | Jao Luiz Liveira Jaques Candino Moreira | Luziane Pecanha |
| 4909 | Jessika De Souza Rizzo | Palblo Zampieri |
| 4961 | Joao Emmanuel Andrade Paixao | Ambrosio Correa |
| 5160 | Jonas Corteletti | Marcos Antonio Dos Santos |
| 5249 | Jose Eduardo Tuao Carvalho | Thiago Coelho Da Silva |
| 5255 | Jose Emerson Oliveira Santos | Yago De Medeiros Borges |
| 5257 | Jose Eustaquio Nunes | Maycon Da Silva Delatorri Avaliacao Dos Indicadores Da Qualidade Baseados Na Metodologia Do Balanced Scorecard |
| 5346 | Josivania Dos Reis Ferreira | Roseneia Simoes Da V Olindino |
| 5395 | Julia Marques Lana | Thamires Oliveira Felipe |
| 5447 | Juliana De Oliveira Moreira | Laiz Rizzi Andriolli |
| 5477 | Juliana Santos Faber | Juliano Fernandes Merlo |
| 5482 | Juliana Teixeira Pestana | Mariana Silder Callegario |
| 5502 | Juliany Dettmann Dos Santos | Sandra Maria Rodrigues |
| 5528 | Julio De Souza Correia | Felipe Do Carmo Grigorio |
| 5558 | Jussara Farias Fardin | Lucas Frizera Encarnacao |
| 5588 | Kamila Nichio Cerdeiro | Luciana Martins Vieira |
| 5641 | Karla Caetano Nascimento | Priscila Dalapicola Borges |
| 5884 | Larissa Brandao Vitorio | Alexandro Brandao Vitorio |
| 5887 | Larissa Costalonga Vivaldi | Debora Coelho Lima |
| 5895 | Larissa Gomes Almeida | Larissa Simiao Sossai |
| 6020 | Leonardo B Altoe Milton Luiz R Telles | Vinicios Da Silva |
| 6124 | Leticia M Santana Felipe | Renata S Castro |
| 6128 | Leticia Nayara De Lima Costa | Luana Marin Ribeiro |
| 6194 | Livia Tononi Aurich | Gustavo Da Costa Zucolotto |
| 6198 | Liza De Oliveira Dos Santos | Marcella Lopes Alvarenga |
| 6271 | Luan J Souza De Oliveira | Tiago Bastos Do Espirito Santo |
| 6294 | Luana Lunara Da Fonseca | Sara Santos Siqueira |
| 6297 | Luana Pereira De Souza | Matheus Brito Santos |
| 6357 | Lucas Dominicini Zorzal | Vinicius Cordeiro Brito Cardoso |
| 6416 | Lucas Ribeiro Carlin | Mauricio Sarmento Rezende |
| 6473 | Luciana Vinco Pereira | Rogerio Panetto Bono |
| 6570 | Luis Henrique Silveira Borges | Allan Robert Teles De Brito |
| 6764 | Manuella Da Costa Ferreira | Priscila Torenzani Silva |
| 6834 | Marcelo Guimaraes Carvalho | Thewcly Da Silva Souza |
| 6880 | Marcia Regina Nunes Ribeiro | Silvana De Azevedo Cruz |
| 6927 | Marco Antonio Bergamini | Diego Mendes Luppi Da Silva |
| 6953 | Marcos Adriano Fernandes Felix Reducao Dos Niveis Atuais De Estoques | Mercadorias Ociosas Atraves Da Melhoria De Processos Na Dalma Pneus Com Serv |
| 7017 | Marcus Vinbicius Macedo Barros | Renata Pavesi Lube |
| 7063 | Maria Clara De Moura | Silva Barcelos |
| 7151 | Maria Julia Coimbra Oliveira Guddi | Silva |
| 7208 | Mariana Biss Mathias | Sueli Moreira Dos Santos |
| 7320 | Mario Romulo Fernandes Claydson Rafalski | Emerson Jeovany |
| 7358 | Marlon Moro Lombardi | Mirlan Moro Lombardi |
| 7501 | Matheus Silva Santos | Thalison Janio Pelegrini |
| 7711 | Mirielly Nunes Quintao Chagas | Victor Silveira Chagas |
| 7747 | Moreno Pinheiro Cunha | Vivian Martins Pontes |
| 8058 | Patricia De Almeida Santana | Wellington Daud Felippe |
| 8076 | Patricia Pinto De Freitas | Fernanda Gabriel Tose |
| 8194 | Pedro Emmanuel Capuchinho De Freitas | Xavier |
| 8235 | Pedro Lucas De Souza Fernandes | Silva |
| 8269 | Pedro Souza Moreira Neto | Priscila Borges Donatelli |
| 8278 | Pericles Rezende Barros | Antonio Marcus Nogueira Lima |
| 8286 | Peterson M Oliveira Da Vitoria | Renan Campagnaro Soprani |
| 8393 | Rafael Costa Digan | Sallis Nazareth Dos Santos |
| 8417 | Rafael Goncalves Ferreira Analise Da Previsao De Demanda | O Lec Dos Produtos De Maior Impacto Financeiro Da Empresa J |
| 8425 | Rafael Lorencao Cabrini | Thiago Mill Bento Alves |
| 8821 | Ricardo Da Silva Rodrigues Teixeira | Thiago Henrique Santos |
| 9056 | Rogeria Seglia Gomide | Shirley Mara Vertuoso Fachetti |
| 9287 | Sanderson Gurgel | Keverson Soares De Oliveira |
| 9393 | Sergio Diniz Abrantes | Mauro Lucio Zauza |
| 9394 | Sergio Diniz Abrantes | Roldao Alves De Souza Junior |
| 9397 | Sergio Felix De Godoy Padronizacao De Processos Na Geracao De Despesa Publica Empenhamento Liquidacao | Pagamento De Despesa Na Prefeitura Municipal De Augusto De Lima Mg |
| 9609 | Suzi Lara Werner | Carlos Henrique G Correia |
| 9635 | Tales Machado Coelho | Thais Mose Nascimento |
| 9711 | Tavares C M Santana | M Ronchetti R Rogerio T P |
| 9721 | Taynara Dos Santos Arpini | Priscila Da C S Braga |
| 9766 | Thais Do Nascimento Cassimiro | Ana Paula De Oliveira Moraes |
| 9793 | Thales Del Puppo Altoe | Thiago Freitas Soares |
| 9883 | Thiago De Oliveira Vallandro | Wanderson Luiz Do C Pulchera |
| 10539 | Winder Borges Vieira | Pamella Roberta Oliveira |

## D — Nome + Título de Trabalho Embutido · 8 casos

> [!WARNING]
> O pipeline capturou o nome do orientando ou autor concatenado ao título do TCC/trabalho num único campo.

| ID | Nome extraível | Título embutido (início) |
|---|---|---|
| 630 | Ana Claudia Pereira Gott | *Controle de estoques com enfase no ponto de pedido...* |
| 1066 | Arlene Batista Da Silva | *Leitura literaria na perspectiva da pedagogia historico critica u...* |
| 1488 | Bruno Meschiatti Vasconcellos | *Desenvolvimento de uma plataforma de aquisicao de sinais cerebrai...* |
| 3638 | Gabriel Campos Januario | *Aplicacao de business intelligence para melhorias na gestao da ma...* |
| 3844 | Geovanete Antonio Da Costa | *Utilizacao do metodo pdca no gerenciamento do consumo de oleo com...* |
| 5548 | Junior Aguilar De Amorim Controle Da Navegacao De Uma Cadeira De Rodas Robotizada Dentro De Um Ambiente Controlado Usando Visao Computacional | *Desenvolvimento de uma interface grafica visual para uma cadeira ...* |
| 8097 | Paula Katharina De Oliveira Lima | *Controle de uma mao robotica a partir de sinais de eletromiografi...* |
| 9719 | Taynara Cristine Rodrigues Dos Santos Construcao De Um | *Sistema de aeroponia automatizado turma ii...* |

## E — Abreviação Bibliográfica / Lista de Autores · 16 casos

> [!NOTE]
> O slug foi gerado a partir de um campo de autoria de artigo no formato ABNT comprimido (ex: `sobrenome-a-b-outro-c-d`).  
> Representa múltiplos autores, não uma única pessoa identificável.

| ID | Slug | Autores prováveis |
|---|---|---|
| 1382 | `broseghini-l-r-anjos-s-c-rodrigues-w-s` | ~3 autores comprimidos |
| 1610 | `campos-l-r-dalfior-l-m-busato-m-l-reis-s-c` | ~4 autores comprimidos |
| 1611 | `campos-t-t-nascimento-l-rossi-r` | ~2 autores comprimidos |
| 1675 | `carlos-eduardo-g-r-alves` | ~2 autores comprimidos |
| 2009 | `correia-a-l-f-moreira-a-s-rafael-d-f-b-origi-j-a` | ~6 autores comprimidos |
| 2417 | `dibai-v-f-tiburcio-t-l-reis-p-t-lacerda-l-c-f-santos-j` | ~5 autores comprimidos |
| 3621 | `freitas-m-c-m-c-nunes-v-g-s` | ~3 autores comprimidos |
| 5100 | `joao-vitor-calmon-c-r-porto` | ~2 autores comprimidos |
| 5427 | `juliana-a-secco-lilian-l-peccini-merilin-m-m-pegoretti` | ~3 autores comprimidos |
| 6001 | `leidiani-o-meireles-leonardo-c-n-batista-rodrigo-a-moteiro` | ~3 autores comprimidos |
| 6008 | `lemos-a-l-s-lopes-c-s-aguiar-b-m-goncalves-p-a` | ~5 autores comprimidos |
| 6945 | `marco-c-c-guimaraes` | ~2 autores comprimidos |
| 7725 | `moises-r-n-ribeiro` | ~2 autores comprimidos |
| 8537 | `ramos-b-v-s-quiterio-j-s-carlos-m-p` | ~4 autores comprimidos |
| 10095 | `vassoler-a-r-sa-b-m-m-patricio-f-t` | ~4 autores comprimidos |
| 10312 | `vitoria-er-santos-h-f-dimas-j-s-lima-m-v-s` | ~3 autores comprimidos |

---

## Duplicatas Suspeitas por Variação Ortográfica *(fora das 239)*

> [!TIP]
> Estes pares não estão nas 239 anomalias acima, mas são candidatos a serem a mesma pessoa com grafia divergente entre sistemas. Revisão manual recomendada.

| ID 1 | Slug 1 | ID 2 | Slug 2 | Variação |
|---|---|---|---|---|
| 3680 | `gabriel-libardi-silva` | 3681 | `gabriel-libardini-silva` | `libardi` vs `libardini` |
| 5266 | `jose-goncalves-pereira-filho` | 5267 | `jose-golcalves-pereira-filho` | `goncalves` vs `golcalves` |
| 9905 | `thiago-machado-de-oliveira` | 9907 | `thiago-machado-oliveira` | com / sem `de` |
| 6343 | `lucas-coutinho-de-oliveira` | 6344 | `lucas-coutinho-de-souza-oliveira` | com / sem `de-souza` |
| 9913 | `thiago-oliveira-dos-santos` | 9915 | `thiago-oliveira-santos` | com / sem `dos` |
| 7082 | `maria-das-gracas-siqueira-pereira` | 7092 | `maria-da-graca-siqueira-pereira` | `das-gracas` vs `da-graca` |

---

*Gerado por análise programática da aba `IDs` de [Matriz_Pessoas_SRC_Horizon_Egressos.xlsx](file:///home/pedrolino7/Documentos/comparaListas/Matriz_Pessoas_SRC_Horizon_Egressos.xlsx)*
