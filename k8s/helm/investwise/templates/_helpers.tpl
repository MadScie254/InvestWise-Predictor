{{/*
Expand the name of the chart.
*/}}
{{- define "investwise.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "investwise.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "investwise.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "investwise.labels" -}}
helm.sh/chart: {{ include "investwise.chart" . }}
{{ include "investwise.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- with .Values.commonLabels }}
{{ toYaml . }}
{{- end }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "investwise.selectorLabels" -}}
app.kubernetes.io/name: {{ include "investwise.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "investwise.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "investwise.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the secret to use
*/}}
{{- define "investwise.secretName" -}}
{{- default (printf "%s-secrets" (include "investwise.fullname" .)) .Values.secrets.name }}
{{- end }}

{{/*
Database URL helper
*/}}
{{- define "investwise.databaseUrl" -}}
{{- if .Values.postgresql.enabled }}
{{- printf "postgresql://%s:%s@%s-postgresql:5432/%s" .Values.postgresql.auth.username .Values.postgresql.auth.password (include "investwise.fullname" .) .Values.postgresql.auth.database }}
{{- else }}
{{- .Values.externalDatabase.url }}
{{- end }}
{{- end }}

{{/*
Redis URL helper
*/}}
{{- define "investwise.redisUrl" -}}
{{- if .Values.redis.enabled }}
{{- if .Values.redis.auth.enabled }}
{{- printf "redis://:%s@%s-redis-master:6379" .Values.redis.auth.password (include "investwise.fullname" .) }}
{{- else }}
{{- printf "redis://%s-redis-master:6379" (include "investwise.fullname" .) }}
{{- end }}
{{- else }}
{{- .Values.externalRedis.url }}
{{- end }}
{{- end }}

{{/*
Common environment variables
*/}}
{{- define "investwise.commonEnv" -}}
- name: ENVIRONMENT
  value: {{ .Values.environment | quote }}
- name: RELEASE_NAME
  value: {{ .Release.Name | quote }}
- name: NAMESPACE
  value: {{ .Release.Namespace | quote }}
{{- end }}

{{/*
Image pull policy
*/}}
{{- define "investwise.imagePullPolicy" -}}
{{- default .Values.imagePullPolicy .Values.global.imagePullPolicy }}
{{- end }}

{{/*
Storage class
*/}}
{{- define "investwise.storageClass" -}}
{{- if .Values.global.storageClass }}
{{- .Values.global.storageClass }}
{{- else }}
{{- .Values.persistence.storageClass }}
{{- end }}
{{- end }}