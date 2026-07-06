[English](README.md) | [Español](README.es.md)

# Morphix

Aplicación web para conversión asíncrona de archivos sin APIs externas de conversión. Frontend React/Vite, API FastAPI, worker de conversión en Python, infraestructura Terraform/Terragrunt y despliegues con GitHub Actions.

Licenciado bajo la [Licencia Apache 2.0](LICENSE).

## Arquitectura

Cuatro límites explícitos: el frontend posee el flujo de usuario, la API posee la coordinación de jobs y la seguridad, el worker posee la ejecución de conversiones, y la infraestructura posee el despliegue, aislamiento, almacenamiento y observabilidad.

```mermaid
flowchart LR
    Browser["Navegador (React/Vite)"] --> CF["CloudFront + S3"]
    Browser -->|HTTP| AGW["API Gateway"]
    AGW --> Lambda["FastAPI Lambda"]
    Lambda --> DDB[("DynamoDB jobs")]
    Lambda -->|URL prefirmada| S3I[("S3 entrada")]
    Lambda -->|inicia| SFN{{"Step Functions"}}
    SFN -->|encola| SQS[("SQS + DLQ")]
    SQS --> ECS["Worker ECS Fargate"]
    ECS -->|descarga| S3I
    ECS -->|convierte| LocalBin["LibreOffice / FFmpeg / ImageMagick"]
    ECS -->|sube| S3O[("S3 salida")]
    ECS -->|callback| SFN
    Lambda -->|URL prefirmada| S3O
```

El flujo de runtime es asíncrono: el frontend se entrega desde S3 a través de CloudFront, la API recibe las solicitudes de job vía API Gateway/Lambda, Step Functions orquesta cada conversión, SQS amortigua la ejecución del worker, y un worker ECS Fargate consume la cola secuencialmente. El navegador nunca recibe credenciales AWS; lee `runtime-config.json` publicado por Terraform para descubrir la URL base de la API y usa URLs prefirmadas para mover archivos directamente hacia/desde S3.

### Frontend — Feature-Sliced Design

`apps/frontend/src` (React 19 + Vite + Tailwind v4 + shadcn/ui, estado de servidor con TanStack Query):

```mermaid
flowchart TB
    app["app<br/>providers · router · estilos"]
    pages["pages<br/>converter"]
    widgets["widgets<br/>workspace · overview · jobs-history · app-shell"]
    features["features<br/>convert · select-format · download · delete-job"]
    entities["entities<br/>job · conversion · user"]
    shared["shared<br/>api · config · ui · lib"]
    app --> pages --> widgets --> features --> entities --> shared
```

- `app`: bootstrap, providers, router, estilos globales.
- `pages`: composiciones a nivel de ruta.
- `widgets`: bloques completos de UI (workspace de conversión, overview, historial de jobs).
- `features`: acciones de usuario con intención de negocio (convertir archivo, seleccionar formato destino, descargar resultado, eliminar job).
- `entities`: modelos de dominio del frontend (jobs, conversiones, contexto de usuario).
- `shared`: cliente HTTP, configuración de entorno, hooks, primitivas de UI, utilidades, tipos.

### API — Arquitectura Hexagonal

`apps/api/src/morphix_api` (FastAPI). Los adaptadores inbound llaman a los casos de uso, los casos de uso dependen de puertos, y los adaptadores outbound implementan esos puertos. El núcleo nunca depende de FastAPI ni de detalles del SDK de AWS.

```mermaid
flowchart RL
    HTTP["adapters/inbound/http<br/>rutas FastAPI · schemas · DI"] --> UC["application/use_cases<br/>create · list · urls · start · delete"]
    UC --> PORTS["application/ports<br/>job repo · object urls · orquestación"]
    OUT["adapters/outbound<br/>DynamoDB · S3 prefirmado · Step Functions"] -.->|implementa| PORTS
    UC --> DOMAIN["domain<br/>conceptos · value objects · políticas · errores"]
    CORE["core<br/>config · seguridad · tiempo"] --> UC
```

### Worker — Clean Architecture orientada a Pipeline

`apps/worker/src/morphix_worker` (Python en ECS Fargate). El ciclo de vida de conversión es un pipeline explícito: cargar job → marcar processing → descargar entrada → convertir → subir salida → persistir estado. El manejo de errores es parte del pipeline, no algo oculto en adaptadores.

```mermaid
flowchart LR
    EP["entrypoints<br/>parsing env de ECS"] --> PIPE["application/pipeline<br/>orquestación por pasos · flujo de errores"]
    PIPE --> WPORTS["application/ports<br/>object storage · job repo · converter · workspace"]
    PIPE --> WDOMAIN["domain<br/>job · result · format · status · políticas"]
    CONV["converters<br/>LibreOffice · FFmpeg · ImageMagick · spreadsheets · PDF"] -.->|implementa| WPORTS
    WOUT["adapters/outbound<br/>S3 · DynamoDB"] -.->|implementa| WPORTS
    WCORE["core<br/>config · logging · workspace · subprocess"] --> PIPE
```

El pipeline depende de puertos, no de S3, DynamoDB, ECS ni binarios específicos — manteniendo la lógica de conversión testeable y las preocupaciones de infraestructura en el borde.

### Infraestructura — Runtime y entrega en AWS

Aprovisionada con módulos Terraform (`infra/blueprints/modules`) y stacks live de Terragrunt (`infra/terraform`). GitHub Actions construye, testea y despliega frontend, paquetes Lambda de la API, imágenes del worker y cambios de infraestructura.

- CloudFront + S3 entregan el frontend.
- API Gateway invoca el adaptador FastAPI Lambda.
- Buckets S3 privados almacenan entrada/salida vía URLs prefirmadas de corta duración.
- Step Functions posee la orquestación, transiciones de estado y callbacks del worker.
- SQS amortigua jobs, reintenta fallos de pickup y mueve mensajes venenosos a una DLQ.
- ECS Fargate ejecuta el worker desde ECR (`desired_count = 1`).
- DynamoDB almacena metadata de jobs, ownership y estado.
- CloudWatch captura logs y telemetría.
- Las variables de runtime del frontend no son inyectadas por workflows; Terraform las publica como runtime config en S3.

## Estructura del repositorio

- `apps/frontend`: UI de conversión React + TypeScript + Vite gestionada con Bun.
- `apps/api`: servicio FastAPI Lambda para jobs, batches, URLs prefirmadas, checks de ownership e inicios de Step Functions.
- `apps/worker`: worker Python dockerizado usando motores de conversión locales.
- `infra/blueprints`: módulos Terraform reutilizables y bootstrap de estado remoto. La state machine vive en el módulo de la API y publica trabajo a la cola de conversión compartida.
- `infra/terraform`: stacks live de Terragrunt.
- `.github/workflows`: CI/CD para infra, frontend y backend. API y worker despliegan desde un workflow backend ordenado.
- `docs/prd-coverage.md`: checklist de cobertura de requisitos del PRD.

Sin `Taskfile.yml` a propósito, ajustándose al scope MVP.

## Uso local

```bash
docker compose up --build
```

El sistema completo corre localmente en Docker Compose: frontend (Vite dev con HMR), API FastAPI en uvicorn con reload, worker de conversión sondeando SQS, y LocalStack emulando DynamoDB, S3, SQS y DynamoDB Streams. Un contenedor `init` provisiona las tablas, buckets y colas antes de que arranquen la API y el worker.

```mermaid
flowchart LR
    Browser["Navegador (Vite :5173)"] -->|HTTP + X-User-Id| API["FastAPI :8000<br/>uvicorn --reload"]
    Browser <-->|WebSocket /ws| API
    Browser -->|PUT/GET prefirmado| LS[("LocalStack :4566<br/>S3 entrada/salida")]
    API -->|marca QUEUED + encola| LS
    API -->|sondea DynamoDB Streams| LS
    Worker["Worker<br/>queue_worker"] -->|sondea SQS| LS
    Worker -->|descarga entrada| LS
    Worker -->|convierte| LocalBin["LibreOffice / FFmpeg / ImageMagick"]
    Worker -->|sube salida + marca COMPLETED| LS
```

1. Abrí http://localhost:5173. El frontend se entrega con un `runtime-config.json` sintético que lo conecta a la API en `http://localhost:8000` y al WebSocket de tiempo real en `ws://localhost:8000/ws`.
2. Subí un archivo soportado desde la UI. La API emite una URL prefirmada reescrita a `http://localhost:4566` para que el navegador suba directo a S3 en LocalStack.
3. Iniciá la conversión. El `LocalSQSConversionOrchestrator` encola el job en SQS y lo marca `QUEUED` en DynamoDB — sin Step Functions.
4. El worker toma el mensaje, ejecuta el pipeline de conversión (descarga → convierte → sube) y persiste `PROCESSING → COMPLETED` (o `FAILED`) en DynamoDB.
5. Un poller en la API lee DynamoDB Streams y pushea eventos `job.updated` por WebSocket, así la UI se actualiza en tiempo real.

El hot-reload aplica a la API (`uvicorn --reload`) y al frontend (Vite HMR). Para aplicar cambios del worker, ejecutá `docker compose restart worker`. Usá `docker compose down -v` para limpiar el estado de LocalStack; `docker compose down` lo persiste en el volumen.

Docs de la API: http://localhost:8000/docs. El header `X-User-Id` (cualquier string ≤128 caracteres) identifica al dueño del job y se guarda en `localStorage` entre sesiones.

## Límites MVP

- Tamaño máx. de upload: configurable, default `100 MB`.
- Retención de entrada: `1 día`. Retención de salida: `7 días`.
- Timeout del worker: configurable, default `900 segundos`.
- Los motores de conversión son binarios locales o librerías Python empaquetadas en la imagen del worker.

## Deploy

1. Configura `AWS_ACCESS_KEY_ID` y `AWS_SECRET_ACCESS_KEY` como secrets del repositorio. `AWS_REGION` está fija en los workflows como `us-east-1`.
2. Ejecuta `.github/workflows/infra-lifecycle.yml` con `plan` o `apply`. Hace bootstrap del bucket de estado Terraform y la tabla de lock en DynamoDB si no existen. Los flows de destroy detienen conversiones en curso y vacían buckets/imagenes ECR antes de que Terragrunt destruya los stacks.
3. Despliega backend con `.github/workflows/backend-deploy.yml`, seleccionando `api`, `worker` o `both`. En push, detecta cambios de rutas y despliega solo los componentes afectados. La Lambda de la API se empaqueta con `apps/api/scripts/build_lambda.sh` (zip de función + zip de dependencias como Lambda Layer); el worker es una imagen Docker/ECR para ECS Fargate.

Los módulos Terraform usan buckets S3 privados, URLs prefirmadas de corta duración, DynamoDB TTL, CloudWatch logs, callbacks de Step Functions, políticas de redrive de SQS, aislamiento ECS Fargate y límites de estado separados.
