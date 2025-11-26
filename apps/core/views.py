from django.http import JsonResponse


def health(request):
	"""Simple health check endpoint for readiness/liveness probes."""
	return JsonResponse({"status": "ok"})
