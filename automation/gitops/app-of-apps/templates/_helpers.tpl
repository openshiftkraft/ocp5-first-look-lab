{{/*
Common sync policy for child Applications.
Provides automated sync with prune, selfHeal, retry with backoff, and standard syncOptions.
*/}}
{{- define "app-of-apps.syncPolicy" -}}
syncPolicy:
  automated:
    prune: true
    selfHeal: true
  retry:
    backoff:
      duration: 5s
      factor: 2
      maxDuration: 2m0s
    limit: 30
  syncOptions:
    - CreateNamespace=true
    - RespectIgnoreDifferences=true
    - SkipDryRunOnMissingResource=true
{{- end }}

{{/*
Returns the operator catalog source name.
All operators come from the GA "redhat-operators" catalog of OpenShift 5.
The 4.22 snapshot (catalogSource) is no longer used by any subscription.
*/}}
{{- define "app-of-apps.operatorSource" -}}
redhat-operators
{{- end -}}

{{/*
Common Application metadata with foreground finalizer.
Usage: {{ include "app-of-apps.metadata" (dict "name" "my-app" "namespace" .Values.argocd.namespace "syncWave" "0") }}
*/}}
{{- define "app-of-apps.metadata" -}}
metadata:
  name: {{ .name }}
  namespace: {{ .namespace }}
  labels:
    app.kubernetes.io/part-of: app-of-apps
  annotations:
    argocd.argoproj.io/sync-wave: "{{ .syncWave }}"
  finalizers:
    - resources-finalizer.argocd.argoproj.io/foreground
{{- end }}
