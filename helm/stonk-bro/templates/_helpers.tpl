{{- define "stonk.labels" -}}
app.kubernetes.io/name: stonk-bro
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/* selector labels for one component: include "stonk.sel" (list . "api") */}}
{{- define "stonk.sel" -}}
{{- $root := index . 0 -}}
app.kubernetes.io/name: stonk-bro
app.kubernetes.io/instance: {{ $root.Release.Name }}
app.kubernetes.io/component: {{ index . 1 }}
{{- end }}

{{- define "stonk.image" -}}
{{ index . 1 }}:{{ (index . 0).Values.image.tag }}
{{- end }}

{{/* env shared by every backend container */}}
{{- define "stonk.backendEnv" -}}
env:
  - name: REDIS_URL
    value: redis://{{ .Release.Name }}-redis:6379
  - name: ENVIRONMENT
    value: {{ .Values.config.environment | quote }}
  - name: LOG_LEVEL
    value: {{ .Values.config.logLevel | quote }}
  - name: TFSA_BIRTH_YEAR
    value: {{ .Values.config.tfsaBirthYear | quote }}
  - name: TFSA_INITIAL_CONTRIBUTION_ROOM
    value: {{ .Values.config.tfsaInitialContributionRoom | quote }}
envFrom:
  - secretRef:
      name: {{ .Release.Name }}-env
{{- end }}
