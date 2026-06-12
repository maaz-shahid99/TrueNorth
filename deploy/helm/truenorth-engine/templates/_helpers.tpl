{{- define "truenorth-engine.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "truenorth-engine.fullname" -}}
{{- printf "%s-%s" .Release.Name (include "truenorth-engine.name" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "truenorth-engine.labels" -}}
app.kubernetes.io/name: {{ include "truenorth-engine.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{- define "truenorth-engine.selectorLabels" -}}
app.kubernetes.io/name: {{ include "truenorth-engine.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- define "truenorth-engine.secretName" -}}
{{- if .Values.secrets.existingSecret -}}
{{- .Values.secrets.existingSecret -}}
{{- else -}}
{{- include "truenorth-engine.fullname" . -}}
{{- end -}}
{{- end -}}
