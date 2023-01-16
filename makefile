deploy-http: @echo "Deploying cloud functions"
	gcloud functions deploy stats-http-function \
	--gen2 \
	--runtime=python310 \
	--region=eu-west1 \
	--source=. \
	--entry-point=stats \
	--trigger-http \
	--allow-unauthenticated

