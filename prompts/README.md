# Prompts

| Archivo | Agente | Palabras | Uso |
|---|---|---|---|
| [`generador.txt`](generador.txt) | Generador STRIDE | **96** | **Prompt público** del reto: sirve en cualquier LLM. En WF-2 es el *system prompt* del generador |
| [`revisor.txt`](revisor.txt) | Revisor | 188 | Interno (WF-2) |
| [`mitigacion.txt`](mitigacion.txt) | Mitigación | 91 | Interno (WF-2) |
| [`abstraccion.txt`](abstraccion.txt) | Abstracción | 105 | Interno (WF-3) |
| [`esquemas.json`](esquemas.json) | Todos | — | Esquema JSON de la respuesta de cada agente (se envía en `output_config.format`) |

Conteo: `wc -w prompts/*.txt`. El límite de 100 palabras del reto aplica al prompt público (`generador.txt`).

## Prompt público (≤100 palabras)

```text
Actúa como analista de seguridad de aplicaciones. Recibirás uno o más casos de uso de un ecommerce. Para cada caso de uso genera al menos un caso de abuso usando STRIDE. Cada caso de abuso debe indicar: el ID del caso de uso vinculado, la categoría STRIDE, el actor (cliente, atacante externo o empleado interno), las precondiciones, cómo ocurre paso a paso sobre componentes y datos concretos, el vector práctico (acción, herramienta y dato manipulado; no basta un CWE, CVE o riesgo genérico) y el impacto. Si recibes contexto, úsalo y no repitas casos ya validados.
```

### Cómo cumple cada requisito

| Requisito | Parte del prompt |
|---|---|
| B1 · No más de 100 palabras | 96 palabras |
| B2 · Acepta uno o más casos de uso | "Recibirás uno o más casos de uso" |
| B3 · Al menos un caso de abuso por caso de uso | "Para cada caso de uso genera al menos un caso de abuso" |
| B4a · Referencia el caso de uso vinculado | "el ID del caso de uso vinculado" |
| B4b · Explica claramente cómo sucede | "cómo ocurre paso a paso sobre componentes y datos concretos" |
| B4c · Vectores prácticos, no solo CWE/CVE/riesgo genérico | "el vector práctico (acción, herramienta y dato manipulado; no basta un CWE, CVE o riesgo genérico)" |

### Cómo usarlo en un LLM público

Se pega el prompt y, debajo, uno o más casos de uso. Ejemplo:

```text
[prompt]

UC-11 · Registro de entrega a domicilio con geolocalización: el repartidor registra la entrega en su app; el registro solo es válido si su ubicación coincide con la de entrega (RN-3). La app envía el registro a logistic y este a delivery-api.

UC-13 · Cancelación posterior a la recepción y devolución: después de recibir el producto, el cliente cancela desde la app; se genera una recolección inversa y se emite el reembolso.
```

En un LLM público la respuesta llega en texto con esos campos. En WF-2 el mismo prompt va acompañado del esquema JSON del agente ([`esquemas.json`](esquemas.json)) en `output_config.format` (*structured outputs* de la API de Claude), así que la respuesta llega estructurada (supuesto S-35).

## Prompts internos

Los prompts del revisor, la mitigación y la abstracción no tienen límite de palabras en el reto. Se mantienen cortos y piden una sola cosa cada uno. El del revisor contiene los criterios R3 a R7 de [`docs/03-arquitectura.md`](../docs/03-arquitectura.md) §5.3; R1 y R2 los revisa código determinista en WF-2, antes de llamar al revisor.

En los cuatro agentes, el contenido variable (caso de uso, contexto, casos a revisar) va **entre etiquetas** y con la indicación de que son datos y no instrucciones. Es una de las defensas contra la inyección de instrucciones a través de la memoria o de un caso de uso en texto libre.
