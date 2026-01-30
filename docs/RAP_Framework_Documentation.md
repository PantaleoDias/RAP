# RAP Framework
## Resilience Acceleration Program
### Framework de Quantificação de Risco Orientado à Resiliência Cibernética

**Versão:** 1.0
**Data:** Janeiro 2025
**Classificação:** Público

---

## Sumário Executivo

O **RAP (Resilience Acceleration Program)** é um framework de quantificação de risco cibernético projetado para organizações que buscam medir, comunicar e gerenciar riscos de segurança de forma quantitativa e orientada à resiliência.

Diferentemente de abordagens qualitativas tradicionais (alto/médio/baixo), o RAP utiliza modelagem estatística baseada no Open FAIR para traduzir riscos em termos financeiros, permitindo decisões de investimento baseadas em dados.

O framework integra três perspectivas complementares:
- **Objetivos de Negócio** (o que a organização precisa)
- **Maturidade de Controles** (o que a organização tem implementado)
- **Realidade Operacional** (como os controles se comportam sob pressão)

---

## 1. Introdução

### 1.1 Propósito

O RAP foi desenvolvido para atender às seguintes necessidades organizacionais:

1. **Quantificar riscos cibernéticos em termos financeiros** para facilitar a comunicação com executivos e o conselho
2. **Integrar múltiplas perspectivas de risco** (negócio, governança e técnica) em uma visão unificada
3. **Priorizar investimentos em segurança** com base em redução de risco esperada
4. **Medir a eficácia de controles** comparando expectativas com resultados reais
5. **Estabelecer uma linguagem comum** entre equipes técnicas, de GRC e de negócio

### 1.2 Escopo

O RAP é aplicável a:
- Organizações de qualquer porte e setor
- Ambientes de TI, OT/ICS e híbridos
- Riscos cibernéticos internos e externos
- Conformidade regulatória (LGPD, GDPR, SOX, PCI-DSS)

### 1.3 Público-Alvo

| Papel | Uso do Framework |
|-------|------------------|
| CISO / CSO | Comunicação de risco ao board, priorização de investimentos |
| Equipe de GRC | Avaliação de controles, conformidade, métricas de maturidade |
| Red Team / Pentesters | Validação de controles, medição de gaps |
| Gestores de Risco | Quantificação financeira, análise de cenários |
| CFO / Executivos | Decisões de investimento baseadas em ROI de segurança |

### 1.4 Relação com Outros Frameworks

O RAP foi projetado para **complementar** (não substituir) frameworks existentes:

```
┌─────────────────────────────────────────────────────────────────┐
│                         RAP Framework                           │
│              (Quantificação e Integração de Risco)              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│   │  Open FAIR   │  │   NIST CSF   │  │  ISO 27001   │         │
│   │  (Método)    │  │  (Funções)   │  │ (Controles)  │         │
│   └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                 │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│   │ MITRE ATT&CK │  │  CIS Controls│  │    LGPD/     │         │
│   │  (Ameaças)   │  │  (Práticas)  │  │    GDPR      │         │
│   └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Fundamentos do Framework

### 2.1 Princípios Orientadores

O RAP é construído sobre cinco princípios fundamentais:

#### Princípio 1: Quantificação sobre Qualificação
> Riscos devem ser expressos em termos mensuráveis (frequência, impacto financeiro) em vez de escalas subjetivas.

**Racional:** Escalas qualitativas (alto/médio/baixo) são ambíguas e não permitem comparação objetiva entre riscos ou cálculo de ROI.

#### Princípio 2: Três Perspectivas Integradas
> A avaliação de risco deve considerar objetivos de negócio, maturidade de governança e validação técnica.

**Racional:** Cada perspectiva isolada oferece visão incompleta. A integração revela gaps entre expectativa e realidade.

#### Princípio 3: Resiliência como Objetivo
> O foco é a capacidade de resistir, detectar, responder e recuperar — não apenas prevenir.

**Racional:** Prevenção perfeita é impossível. Organizações resilientes minimizam impacto e tempo de recuperação.

#### Princípio 4: Simulação sobre Estimativa Pontual
> Usar distribuições probabilísticas e simulação Monte Carlo em vez de valores únicos.

**Racional:** Incerteza é inerente à estimativa de risco. Distribuições capturam essa incerteza de forma mais precisa.

#### Princípio 5: Melhoria Contínua
> Avaliações devem ser repetíveis e comparáveis ao longo do tempo.

**Racional:** Permite medir progresso, identificar tendências e demonstrar valor dos investimentos.

### 2.2 Modelo Conceitual

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        MODELO CONCEITUAL RAP                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                 │
│  │  BUSINESS   │    │  STRATEGY   │    │  OFFENSIVE  │                 │
│  │  STRATEGY   │    │   & RISK    │    │  SECURITY   │                 │
│  │             │    │ GOVERNANCE  │    │             │                 │
│  │ • Objetivos │    │ • Controles │    │ • Testes    │                 │
│  │ • RTO/RPO   │    │ • Políticas │    │ • Simulação │                 │
│  │ • BIA       │    │ • Processos │    │ • Red Team  │                 │
│  │ • Apetite   │    │ • Evidências│    │ • Métricas  │                 │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘                 │
│         │                  │                  │                         │
│         └──────────────────┼──────────────────┘                         │
│                            ▼                                            │
│                  ┌─────────────────┐                                    │
│                  │   ANÁLISE GAP   │                                    │
│                  │  (PLA 3 Níveis) │                                    │
│                  └────────┬────────┘                                    │
│                           │                                             │
│         ┌─────────────────┼─────────────────┐                          │
│         ▼                 ▼                 ▼                          │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐                   │
│  │ FREQUÊNCIA  │   │   IMPACTO   │   │  CONTROLES  │                   │
│  │   (PERT)    │   │   (PERT)    │   │  (Redução)  │                   │
│  └──────┬──────┘   └──────┬──────┘   └──────┬──────┘                   │
│         │                 │                 │                           │
│         └─────────────────┼─────────────────┘                          │
│                           ▼                                             │
│                  ┌─────────────────┐                                    │
│                  │  SIMULAÇÃO      │                                    │
│                  │  MONTE CARLO    │                                    │
│                  └────────┬────────┘                                    │
│                           │                                             │
│                           ▼                                             │
│                  ┌─────────────────┐                                    │
│                  │   MÉTRICAS DE   │                                    │
│                  │     RISCO       │                                    │
│                  │ • Média         │                                    │
│                  │ • VaR 95%       │                                    │
│                  │ • VaR 99%       │                                    │
│                  └─────────────────┘                                    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Componentes do Framework

### 3.1 As Sete Dimensões de Risco Digital

O RAP organiza o risco cibernético em **sete dimensões**, cada uma representando um domínio crítico de resiliência:

#### Dimensão 1: Resiliência e Recuperação
**Definição:** Capacidade da organização de sobreviver, resistir e recuperar-se de incidentes cibernéticos, mantendo operações críticas e minimizando tempo de inatividade.

**Escopo:**
- Backup e recuperação de dados
- Continuidade de negócios
- Disaster Recovery
- Gestão de crises

**Frameworks Relacionados:** ISO 22301, NIST CSF (Recover), ISO 27001 A.17

**Métricas RAP:**
| ID | Métrica | Descrição |
|----|---------|-----------|
| 01 | Tempo de Recuperação de Joias da Coroa | RTO real vs. RTO definido para sistemas críticos |
| 10 | Soberania de Dados e Geo-redundância | Controle sobre localização e jurisdição dos dados |
| 25 | Gestão de Crises e Comunicação | Maturidade dos processos de resposta coordenada |

---

#### Dimensão 2: Proteção de Identidade e Acesso
**Definição:** Controle rigoroso de identidades, credenciais e acessos privilegiados, prevenindo movimentação lateral e comprometimento de contas.

**Escopo:**
- Identity and Access Management (IAM)
- Privileged Access Management (PAM)
- Multi-Factor Authentication (MFA)
- Zero Trust Architecture

**Frameworks Relacionados:** NIST CSF (Protect), ISO 27001 A.9, CIS Controls 5-6

**Métricas RAP:**
| ID | Métrica | Descrição |
|----|---------|-----------|
| 02 | Resistência a Movimentação Lateral | Capacidade de detectar/bloquear lateral movement |
| 03 | Proteção de Credenciais Privilegiadas | Nível de proteção de contas administrativas |
| 04 | Maturidade de Zero Trust | Implementação de verificação contínua |
| 07 | Resiliência Humana (Phishing) | Taxa de sucesso de phishing simulado |

---

#### Dimensão 3: Segurança de Aplicações e Infraestrutura
**Definição:** Hardening de sistemas, segurança em desenvolvimento, gestão de vulnerabilidades e postura de segurança em ambientes cloud e on-premises.

**Escopo:**
- DevSecOps
- Vulnerability Management
- Cloud Security Posture Management (CSPM)
- Detection and Response (EDR/XDR/SIEM)

**Frameworks Relacionados:** OWASP, CIS Controls, NIST SP 800-53, ISO 27001 A.12-14

**Métricas RAP:**
| ID | Métrica | Descrição |
|----|---------|-----------|
| 05 | Cobertura de Gestão de Vulnerabilidades | % de ativos cobertos e MTTR de vulns críticas |
| 06 | Postura de Segurança em Nuvem | Score CSPM de configuração segura |
| 08 | Segurança no Ciclo de Desenvolvimento | Maturidade DevSecOps (SAST, DAST, SCA) |
| 09 | Efetividade de Detecção e Resposta | MTTD e MTTR para incidentes |

---

#### Dimensão 4: Proteção de Dados e Compliance
**Definição:** Privacidade, classificação de dados, conformidade com LGPD/GDPR, prevenção de vazamentos e evidências de compliance.

**Escopo:**
- Data Loss Prevention (DLP)
- Data Classification
- Privacy by Design
- Regulatory Compliance

**Frameworks Relacionados:** LGPD, GDPR, ISO 27701, NIST Privacy Framework

**Métricas RAP:**
| ID | Métrica | Descrição |
|----|---------|-----------|
| 11 | Classificação e Proteção de Dados | Implementação de classificação e controles |
| 12 | Prevenção de Vazamento de Dados | Efetividade de controles DLP |
| 18 | Conformidade GDPR/LGPD/Privacidade | Nível de conformidade com regulações |

---

#### Dimensão 5: Segurança OT/IoT/Industrial
**Definição:** Proteção de ambientes operacionais, sistemas industriais (ICS/SCADA), dispositivos IoT e convergência IT/OT.

**Escopo:**
- IT/OT Segmentation
- ICS/SCADA Security
- IoT Security
- Industrial Protocol Security

**Frameworks Relacionados:** IEC 62443, NIST SP 800-82, NERC CIP

**Métricas RAP:**
| ID | Métrica | Descrição |
|----|---------|-----------|
| 13 | Segmentação IT/OT | Nível de segregação entre ambientes |
| 14 | Visibilidade de Ativos OT/IoT | % de ativos inventariados e monitorados |
| 15 | Resiliência de Sistemas Industriais | Capacidade de manter operações sob ataque |

---

#### Dimensão 6: IA e Ameaças Emergentes
**Definição:** Riscos relacionados à inteligência artificial, deepfakes, modelos de ML adversariais, e novas tecnologias emergentes.

**Escopo:**
- AI/ML Security
- Deepfake Detection
- Adversarial Machine Learning
- AI Governance

**Frameworks Relacionados:** NIST AI RMF, EU AI Act, ISO/IEC 42001, MITRE ATLAS

**Métricas RAP:**
| ID | Métrica | Descrição |
|----|---------|-----------|
| 16 | Segurança de Modelos de IA/ML | Proteção contra ataques adversariais |
| 17 | Detecção de Deepfakes e Fraudes por IA | Capacidade de detectar conteúdo sintético |
| 19 | Governança de IA Responsável | Implementação de ética e transparência em IA |

---

#### Dimensão 7: Gestão de Riscos e Superfície
**Definição:** Visibilidade da superfície de ataque, gestão de terceiros, cadeia de suprimentos, e alinhamento entre investimento e risco.

**Escopo:**
- Attack Surface Management (ASM)
- Third-Party Risk Management (TPRM)
- Supply Chain Security
- Risk Quantification

**Frameworks Relacionados:** NIST CSF (Identify), ISO 27001 A.15, NIST SP 800-161

**Métricas RAP:**
| ID | Métrica | Descrição |
|----|---------|-----------|
| 20 | Visibilidade da Superfície de Ataque | Monitoramento de exposições externas |
| 21 | Gestão de Riscos de Terceiros | Maturidade do programa TPRM |
| 22 | Segurança da Cadeia de Suprimentos | Proteção contra supply chain attacks |
| 23 | Inteligência de Ameaças Operacional | Capacidade de CTI operacional |
| 24 | Alinhamento Investimento x Risco | Demonstração de ROI em segurança |

---

### 3.2 O Modelo de Três Camadas (PLA View)

O diferencial do RAP é a integração de três perspectivas distintas para cada métrica avaliada:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         MODELO PLA (3 CAMADAS)                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  NÍVEL 1 ─────────────────────────────────────────────────────────────  │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     BUSINESS STRATEGY                            │   │
│  │                                                                  │   │
│  │  Responsável: Security Advisory / CISO / Executivos              │   │
│  │                                                                  │   │
│  │  Pergunta Central:                                               │   │
│  │  "Qual é o OBJETIVO de resiliência/compliance para esta métrica, │   │
│  │   dado o contexto de negócio?"                                   │   │
│  │                                                                  │   │
│  │  Outputs:                                                        │   │
│  │  • Business Impact Analysis (BIA)                                │   │
│  │  • Identificação de Joias da Coroa                               │   │
│  │  • Definição de RTO/RPO                                          │   │
│  │  • Apetite e tolerância a risco                                  │   │
│  │  • Requisitos regulatórios                                       │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                    │
│                                    ▼                                    │
│  NÍVEL 2 ─────────────────────────────────────────────────────────────  │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                  STRATEGY & RISK GOVERNANCE                      │   │
│  │                                                                  │   │
│  │  Responsável: Equipe de GRC / Compliance / Auditoria             │   │
│  │                                                                  │   │
│  │  Pergunta Central:                                               │   │
│  │  "Qual é o nível de MATURIDADE de governança/controles que a    │   │
│  │   organização tem hoje para esta métrica?"                       │   │
│  │                                                                  │   │
│  │  Outputs:                                                        │   │
│  │  • Evidências de processos e políticas                           │   │
│  │  • Compliance score por framework (ISO, NIST, CIS)               │   │
│  │  • Resultados de auditorias                                      │   │
│  │  • Documentação de controles                                     │   │
│  │  • Métricas de maturidade                                        │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                    │
│                                    ▼                                    │
│  NÍVEL 3 ─────────────────────────────────────────────────────────────  │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     OFFENSIVE SECURITY                           │   │
│  │                                                                  │   │
│  │  Responsável: Red Team / Pentesters / Purple Team                │   │
│  │                                                                  │   │
│  │  Pergunta Central:                                               │   │
│  │  "Na PRÁTICA, sob ataque, como essa métrica se comporta?        │   │
│  │   O objetivo é atingido?"                                        │   │
│  │                                                                  │   │
│  │  Outputs:                                                        │   │
│  │  • Attack paths identificados                                    │   │
│  │  • Taxa de exploração                                            │   │
│  │  • Tempo real de recuperação                                     │   │
│  │  • Caminhos de falha                                             │   │
│  │  • Métricas de detecção (MTTD/MTTR real)                        │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### 3.2.1 Exemplo Prático: Métrica 01 (Tempo de Recuperação)

```
┌─────────────────────────────────────────────────────────────────────────┐
│  MÉTRICA 01: Tempo de Recuperação de Joias da Coroa                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  NÍVEL 1 - BUSINESS STRATEGY                                            │
│  ├── Score: 8.0/10                                                      │
│  ├── Target: RTO < 2 horas                                              │
│  └── Contexto: "ERP é crítico para faturamento. Cada hora de           │
│                 downtime custa R$ 500.000."                             │
│                                                                         │
│  NÍVEL 2 - STRATEGY & RISK GOVERNANCE                                   │
│  ├── Score: 7.0/10                                                      │
│  ├── Evidências: Plano de DR documentado, backups testados              │
│  │               trimestralmente, runbooks atualizados                  │
│  └── Gap: Processo depende de conhecimento tácito de 2 pessoas          │
│                                                                         │
│  NÍVEL 3 - OFFENSIVE SECURITY                                           │
│  ├── Score: 5.0/10                                                      │
│  ├── Resultado Real: Recuperação levou 4 horas em simulação             │
│  └── Achados: Restore de DB demorou mais que esperado,                  │
│               documentação desatualizada, dependência de fornecedor     │
│                                                                         │
│  ═══════════════════════════════════════════════════════════════════    │
│                                                                         │
│  ANÁLISE DE GAP                                                         │
│  ├── Gap Objetivo vs. Realidade: 2h (target) vs. 4h (real) = +100%     │
│  ├── Gap Score: 8.0 - 5.0 = 3.0 pontos                                 │
│  └── Fator de Gap: 1.45 (ELEVADO)                                       │
│                                                                         │
│  IMPLICAÇÃO DE RISCO                                                    │
│  └── "ELEVADO - Gap significativo entre objetivo e realidade.           │
│       Requer atenção imediata."                                         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### 3.2.2 Cálculo do Fator de Gap

O fator de gap é calculado comparando as três camadas e determina como os parâmetros de frequência e impacto são ajustados:

```
Gap_BS_OS = max(0, Score_BusinessStrategy - Score_OffensiveSecurity)
Gap_GRC_OS = max(0, Score_GRC - Score_OffensiveSecurity)

Combined_Gap = (Gap_BS_OS × 0.6 + Gap_GRC_OS × 0.4) / 10

Gap_Factor = 0.5 + (Combined_Gap × 1.5)
```

**Interpretação do Fator de Gap:**

| Fator | Classificação | Significado |
|-------|---------------|-------------|
| < 0.7 | BAIXO | Realidade excede expectativas |
| 0.7 - 1.0 | MODERADO | Próximo aos objetivos |
| 1.0 - 1.3 | ELEVADO | Gap entre objetivo e realidade |
| 1.3 - 1.6 | ALTO | Gap significativo requer atenção |
| > 1.6 | CRÍTICO | Desvio maior dos objetivos |

---

### 3.3 Modelo de Quantificação de Risco

O RAP utiliza um modelo de quantificação inspirado no Open FAIR:

#### 3.3.1 Componentes do Modelo

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    MODELO DE QUANTIFICAÇÃO RAP                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│                        ┌─────────────────┐                              │
│                        │  CENÁRIO DE     │                              │
│                        │     RISCO       │                              │
│                        └────────┬────────┘                              │
│                                 │                                       │
│              ┌──────────────────┴──────────────────┐                   │
│              ▼                                     ▼                   │
│     ┌─────────────────┐                   ┌─────────────────┐          │
│     │   FREQUÊNCIA    │                   │    IMPACTO      │          │
│     │   DE EVENTO     │                   │   FINANCEIRO    │          │
│     │                 │                   │                 │          │
│     │  Eventos/Ano    │                   │  R$/Evento      │          │
│     └────────┬────────┘                   └────────┬────────┘          │
│              │                                     │                   │
│              ▼                                     ▼                   │
│     ┌─────────────────┐                   ┌─────────────────┐          │
│     │  DISTRIBUIÇÃO   │                   │  DISTRIBUIÇÃO   │          │
│     │     PERT        │                   │     PERT        │          │
│     │                 │                   │                 │          │
│     │ • Mínimo        │                   │ • Mínimo        │          │
│     │ • Mais Provável │                   │ • Mais Provável │          │
│     │ • Máximo        │                   │ • Máximo        │          │
│     └────────┬────────┘                   └────────┬────────┘          │
│              │                                     │                   │
│              └──────────────────┬──────────────────┘                   │
│                                 │                                       │
│                                 ▼                                       │
│                        ┌─────────────────┐                              │
│                        │   SIMULAÇÃO     │                              │
│                        │  MONTE CARLO    │                              │
│                        │                 │                              │
│                        │  N = 10.000+    │                              │
│                        │  iterações      │                              │
│                        └────────┬────────┘                              │
│                                 │                                       │
│                                 ▼                                       │
│                        ┌─────────────────┐                              │
│                        │  DISTRIBUIÇÃO   │                              │
│                        │  DE PERDA       │                              │
│                        │  ANUAL          │                              │
│                        └────────┬────────┘                              │
│                                 │                                       │
│         ┌───────────────────────┼───────────────────────┐              │
│         ▼                       ▼                       ▼              │
│  ┌─────────────┐         ┌─────────────┐         ┌─────────────┐       │
│  │   MÉDIA     │         │   VaR 95%   │         │   VaR 99%   │       │
│  │  (EAL)      │         │             │         │             │       │
│  └─────────────┘         └─────────────┘         └─────────────┘       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### 3.3.2 Distribuição PERT

A distribuição PERT (Program Evaluation and Review Technique) é utilizada para modelar incerteza em estimativas de três pontos:

**Parâmetros:**
- **Mínimo (a):** Valor otimista
- **Mais Provável (m):** Valor modal
- **Máximo (b):** Valor pessimista

**Fórmula da Média PERT:**
```
E[X] = (a + 4m + b) / 6
```

**Vantagens sobre Triangular:**
- Suaviza as caudas da distribuição
- Concentra mais massa de probabilidade ao redor do modo
- Mais adequada para estimativas de especialistas

#### 3.3.3 Simulação Monte Carlo

Para cada iteração da simulação:

```python
Para i de 1 até N_iterações:
    # 1. Amostrar frequência anual
    freq_i = amostra_PERT(freq_min, freq_ml, freq_max)

    # 2. Determinar número de eventos (Poisson)
    n_eventos = Poisson(freq_i)

    # 3. Para cada evento, amostrar impacto
    perda_anual_i = 0
    Para j de 1 até n_eventos:
        impacto_j = amostra_PERT(impact_min, impact_ml, impact_max)
        perda_anual_i += impacto_j

    # 4. Registrar perda anual
    perdas[i] = perda_anual_i

# Calcular estatísticas
média = mean(perdas)
var_95 = percentile(perdas, 95)
var_99 = percentile(perdas, 99)
```

#### 3.3.4 Métricas de Saída

| Métrica | Definição | Uso |
|---------|-----------|-----|
| **Média (EAL)** | Expectativa de perda anual | Orçamento de risco, comparação de cenários |
| **Mediana** | Valor central da distribuição | Cenário "típico" |
| **VaR 90%** | 90% dos anos terão perdas menores | Planejamento conservador |
| **VaR 95%** | 95% dos anos terão perdas menores | Padrão de mercado para risco |
| **VaR 99%** | 99% dos anos terão perdas menores | Cenários de estresse |
| **P(Loss > 0)** | Probabilidade de qualquer perda | Frequência de incidentes |

---

## 4. Implementação do Framework

### 4.1 Ciclo de Vida da Avaliação RAP

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     CICLO DE AVALIAÇÃO RAP                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│     ┌───────────┐                                                       │
│     │   FASE 1  │                                                       │
│     │  ESCOPO   │◄────────────────────────────────────────┐            │
│     └─────┬─────┘                                         │            │
│           │                                               │            │
│           ▼                                               │            │
│     ┌───────────┐                                         │            │
│     │   FASE 2  │                                         │            │
│     │  COLETA   │                                         │            │
│     └─────┬─────┘                                         │            │
│           │                                               │            │
│           ▼                                               │            │
│     ┌───────────┐                                         │            │
│     │   FASE 3  │                                         │            │
│     │  ANÁLISE  │                                         │            │
│     └─────┬─────┘                                         │            │
│           │                                               │            │
│           ▼                                               │            │
│     ┌───────────┐                                         │            │
│     │   FASE 4  │                                         │            │
│     │ SIMULAÇÃO │                                         │            │
│     └─────┬─────┘                                         │            │
│           │                                               │            │
│           ▼                                               │            │
│     ┌───────────┐                                         │            │
│     │   FASE 5  │                                         │            │
│     │  REPORTE  │                                         │            │
│     └─────┬─────┘                                         │            │
│           │                                               │            │
│           ▼                                               │            │
│     ┌───────────┐                                         │            │
│     │   FASE 6  │                                         │            │
│     │  REVISÃO  │─────────────────────────────────────────┘            │
│     └───────────┘                                                       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Fase 1: Definição de Escopo

**Objetivos:**
- Identificar ativos críticos (Joias da Coroa)
- Selecionar dimensões e métricas relevantes
- Definir cenários de risco prioritários
- Estabelecer stakeholders e responsáveis

**Entregáveis:**
- [ ] Lista de ativos críticos com classificação
- [ ] Seleção de métricas RAP aplicáveis
- [ ] Definição de cenários de risco
- [ ] Matriz RACI de responsabilidades

**Template de Cenário:**

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| ID | Identificador único | R001 |
| Nome | Nome descritivo | Ransomware em ERP |
| Métrica RAP | ID da métrica relacionada | 01 |
| Dimensão | Dimensão de risco | 1 - Resiliência |
| Ativo | Sistema/processo afetado | SAP ERP |
| Ameaça | Tipo de ameaça | Ransomware |
| Descrição | Descrição detalhada | Criptografia de banco de dados crítico |

### 4.3 Fase 2: Coleta de Dados

**Fontes de Dados por Camada:**

| Camada | Fonte | Método de Coleta |
|--------|-------|------------------|
| Business Strategy | BIA, Políticas, Entrevistas | Workshop com executivos |
| GRC | Auditorias, Documentação, Tools | Revisão documental, questionários |
| Offensive Security | Pentests, Red Team, Simulações | Relatórios técnicos, métricas |

**Questionário de Avaliação (exemplo para Métrica 01):**

```
BUSINESS STRATEGY
├── Q1: Qual é o RTO definido para este sistema? _____ horas
├── Q2: Este RTO está formalmente documentado? [ ] Sim [ ] Não
├── Q3: Qual o impacto financeiro por hora de downtime? R$ _____
└── Q4: Qual o score de criticidade (1-10)? _____

STRATEGY & RISK GOVERNANCE
├── Q1: Existe plano de DR documentado? [ ] Sim [ ] Não
├── Q2: Frequência de testes de DR? [ ] Mensal [ ] Trimestral [ ] Anual [ ] Nunca
├── Q3: % de backups com teste de restore validado? _____%
└── Q4: Qual o score de maturidade (1-10)? _____

OFFENSIVE SECURITY
├── Q1: Última simulação de DR realizada em: __/__/____
├── Q2: Tempo real de recuperação na última simulação: _____ horas
├── Q3: Problemas identificados na simulação: _____________________
└── Q4: Qual o score de efetividade real (1-10)? _____
```

### 4.4 Fase 3: Análise de Gap

**Processo:**

1. **Consolidar scores** das três camadas
2. **Calcular gaps** entre camadas
3. **Determinar fator de gap** usando fórmula padrão
4. **Classificar risco** (Baixo/Moderado/Elevado/Alto/Crítico)
5. **Mapear para parâmetros** de frequência e impacto

**Matriz de Conversão Score → Parâmetros:**

| Score Combinado | Fator de Frequência | Fator de Impacto |
|-----------------|---------------------|------------------|
| 9-10 | 0.2x | 0.3x |
| 7-8 | 0.5x | 0.5x |
| 5-6 | 1.0x | 1.0x |
| 3-4 | 2.0x | 1.5x |
| 1-2 | 5.0x | 3.0x |

### 4.5 Fase 4: Simulação

**Parâmetros de Entrada:**

```csv
scenario_id,scenario_name,metric_id,freq_min,freq_most,freq_max,impact_min,impact_most,impact_max,currency
R001,Ransomware ERP,01,0.1,0.3,0.7,100000,500000,3000000,BRL
```

**Configuração da Simulação:**

| Parâmetro | Valor Recomendado | Descrição |
|-----------|-------------------|-----------|
| N_iterações | 10.000 - 100.000 | Número de simulações Monte Carlo |
| Distribuição | PERT | Tipo de distribuição para amostragem |
| Lambda | 4.0 | Parâmetro de forma PERT |
| Seed | Definido | Para reprodutibilidade |

**Execução:**
```bash
myrap run --input cenarios.csv --output resultados.csv --iterations 20000
```

### 4.6 Fase 5: Relatório

**Estrutura do Relatório Executivo:**

```
1. SUMÁRIO EXECUTIVO
   ├── Principais riscos identificados
   ├── Exposição financeira total
   └── Recomendações prioritárias

2. VISÃO GERAL DE RISCO
   ├── Distribuição por dimensão
   ├── Top 10 cenários por VaR 95%
   └── Tendências vs. avaliação anterior

3. ANÁLISE POR CENÁRIO
   ├── Visão PLA (3 níveis)
   ├── Análise de gap
   ├── Parâmetros de simulação
   └── Resultados (média, VaR)

4. RECOMENDAÇÕES
   ├── Controles prioritários
   ├── Investimentos recomendados
   └── ROI estimado

5. ANEXOS
   ├── Metodologia detalhada
   ├── Dados de entrada
   └── Resultados completos
```

**Exemplo de Visualização:**

```
TOP 5 RISCOS POR EXPOSIÇÃO ANUAL ESPERADA
═══════════════════════════════════════════════════════════════════

#1 │ Ransomware Attack on ERP
   │ Média: R$ 425.000 │ VaR 95%: R$ 1.850.000 │ VaR 99%: R$ 2.950.000
   │ [████████████████████░░░░░░░░░░] Gap: ELEVADO

#2 │ Data Breach via Phishing
   │ Média: R$ 312.000 │ VaR 95%: R$ 980.000 │ VaR 99%: R$ 1.420.000
   │ [██████████████████░░░░░░░░░░░░] Gap: ALTO

#3 │ Supply Chain Compromise
   │ Média: R$ 285.000 │ VaR 95%: R$ 1.200.000 │ VaR 99%: R$ 3.100.000
   │ [████████████████░░░░░░░░░░░░░░] Gap: MODERADO

#4 │ Cloud Misconfiguration
   │ Média: R$ 198.000 │ VaR 95%: R$ 750.000 │ VaR 99%: R$ 1.100.000
   │ [█████████████░░░░░░░░░░░░░░░░░] Gap: ELEVADO

#5 │ Privileged Account Compromise
   │ Média: R$ 165.000 │ VaR 95%: R$ 620.000 │ VaR 99%: R$ 1.050.000
   │ [███████████░░░░░░░░░░░░░░░░░░░] Gap: ALTO

───────────────────────────────────────────────────────────────────
TOTAL PORTFOLIO
Exposição Anual Esperada: R$ 1.385.000
VaR 95% Agregado: R$ 4.200.000
═══════════════════════════════════════════════════════════════════
```

### 4.7 Fase 6: Revisão e Melhoria

**Frequência Recomendada:**
- **Avaliação Completa:** Anual
- **Atualização de Cenários:** Trimestral
- **Revisão de Métricas:** Após incidentes significativos
- **Recalibração de Parâmetros:** Semestral

**Métricas de Evolução:**

| KPI | Descrição | Meta |
|-----|-----------|------|
| Δ EAL | Variação da exposição anual | Redução de 15%/ano |
| Δ Gap | Variação do fator de gap médio | Redução de 0.1/ano |
| Cobertura | % de ativos críticos avaliados | > 90% |
| Atualização | % de cenários atualizados | 100%/trimestre |

---

## 5. Governança do Framework

### 5.1 Papéis e Responsabilidades

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    ESTRUTURA DE GOVERNANÇA RAP                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│                        ┌─────────────────┐                              │
│                        │   COMITÊ DE     │                              │
│                        │     RISCO       │                              │
│                        │   (Executivo)   │                              │
│                        └────────┬────────┘                              │
│                                 │ Aprova                                │
│                                 ▼                                       │
│                        ┌─────────────────┐                              │
│                        │   RAP PROGRAM   │                              │
│                        │     OWNER       │                              │
│                        │    (CISO)       │                              │
│                        └────────┬────────┘                              │
│                                 │ Coordena                              │
│         ┌───────────────────────┼───────────────────────┐              │
│         ▼                       ▼                       ▼              │
│  ┌─────────────┐         ┌─────────────┐         ┌─────────────┐       │
│  │  BUSINESS   │         │    GRC      │         │  OFFENSIVE  │       │
│  │  STRATEGY   │         │    TEAM     │         │  SECURITY   │       │
│  │    LEAD     │         │    LEAD     │         │    LEAD     │       │
│  └─────────────┘         └─────────────┘         └─────────────┘       │
│        │                       │                       │               │
│        ▼                       ▼                       ▼               │
│  • Security Advisory     • Analistas GRC         • Red Team            │
│  • Business Analysts     • Compliance            • Pentesters          │
│  • Risk Managers         • Auditoria             • Purple Team         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Matriz RACI

| Atividade | Comitê | CISO | BS Lead | GRC Lead | OS Lead |
|-----------|--------|------|---------|----------|---------|
| Definir escopo | A | R | C | C | C |
| Coletar dados BS | I | A | R | C | I |
| Coletar dados GRC | I | A | C | R | I |
| Coletar dados OS | I | A | I | C | R |
| Executar simulação | I | A | C | R | C |
| Validar resultados | A | R | C | C | C |
| Aprovar relatório | A | R | C | C | C |
| Definir ações | A | R | C | C | C |

**Legenda:** R = Responsável, A = Aprovador, C = Consultado, I = Informado

### 5.3 Política de Dados

**Classificação dos Dados RAP:**
- Cenários de risco: **CONFIDENCIAL**
- Resultados de simulação: **CONFIDENCIAL**
- Relatórios executivos: **RESTRITO**
- Metodologia: **INTERNO**

**Retenção:**
- Dados de avaliação: 5 anos
- Relatórios: 7 anos
- Logs de simulação: 1 ano

---

## 6. Referências e Recursos

### 6.1 Frameworks Relacionados

| Framework | Relação com RAP |
|-----------|-----------------|
| Open FAIR | Metodologia de quantificação (base) |
| NIST CSF | Funções de segurança (estrutura) |
| ISO 27001 | Controles de segurança (referência) |
| ISO 22301 | Continuidade de negócios (dimensão 1) |
| IEC 62443 | Segurança industrial (dimensão 5) |
| NIST AI RMF | Riscos de IA (dimensão 6) |
| MITRE ATT&CK | Táticas e técnicas (cenários) |

### 6.2 Ferramentas de Referência

| Ferramenta | Uso | Link |
|------------|-----|------|
| pyfair | Implementação FAIR em Python | github.com/Hive-Systems/pyfair |
| riskquant | Quantificação de risco (Netflix) | github.com/Netflix-Skunkworks/riskquant |
| evaluator | Avaliação Open FAIR em R | github.com/davidski/evaluator |

### 6.3 Bibliografia

1. Freund, J., & Jones, J. (2015). *Measuring and Managing Information Risk: A FAIR Approach*. Butterworth-Heinemann.

2. Hubbard, D. W. (2014). *How to Measure Anything in Cybersecurity Risk*. Wiley.

3. The Open Group. (2017). *Open FAIR Risk Taxonomy (O-RT) Standard*.

4. NIST. (2018). *Framework for Improving Critical Infrastructure Cybersecurity*.

---

## Apêndice A: Glossário

| Termo | Definição |
|-------|-----------|
| **BIA** | Business Impact Analysis - Análise de impacto no negócio |
| **EAL** | Expected Annual Loss - Perda anual esperada |
| **FAIR** | Factor Analysis of Information Risk |
| **Gap Factor** | Fator multiplicador baseado na diferença entre camadas |
| **Joias da Coroa** | Ativos mais críticos da organização |
| **Monte Carlo** | Método de simulação estatística com amostragem aleatória |
| **PERT** | Program Evaluation and Review Technique - Distribuição probabilística |
| **PLA** | Performance Level Agreement - Acordo de nível de desempenho |
| **RTO** | Recovery Time Objective - Objetivo de tempo de recuperação |
| **RPO** | Recovery Point Objective - Objetivo de ponto de recuperação |
| **VaR** | Value at Risk - Valor em risco em determinado percentil |

---

## Apêndice B: Templates

### B.1 Template de Cenário de Risco

```csv
scenario_id,scenario_name,metric_id,metric_name,dimension_id,asset,threat,description,freq_min,freq_most,freq_max,impact_min,impact_most,impact_max,currency
```

### B.2 Template de Avaliação de Camadas

```csv
metric_id,layer,score,target_value,actual_value,confidence,evidence,notes,assessor,assessment_date
```

---

**Documento preparado por:** RAP Framework Team
**Versão:** 1.0
**Última atualização:** Janeiro 2025

---

*Este documento é parte integrante do RAP Framework e deve ser utilizado em conjunto com a implementação técnica e os guias de uso.*
