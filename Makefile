build:
	docker build -t cross/observability/newrelic-migration-exporter:$(version) .

tag-image:
	docker tag newrelic-migration-exporter:$(version) 073521391622.dkr.ecr.us-east-1.amazonaws.com/cross/observability/newrelic-migration-exporter:$(version)

push-image:
	docker push 073521391622.dkr.ecr.us-east-1.amazonaws.com/cross/observability/newrelic-migration-exporter:$(version)

release: build tag-image push-image