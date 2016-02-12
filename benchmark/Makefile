all:
	make run

workdir:
	mkdir -p workdir

clean:
	rm -rf workdir

workdir/client-config.json: client-config.json workdir
	cp -n $< $@

workdir/requests-config.json: requests-config.json workdir
	test -e $@ || (cp $< $@ && python generate_requests.py workdir/requests-config.json)


run: workdir/client-config.json workdir/requests-config.json
	@echo "Before running be sure to modify workdir/client-config.json"
	@echo "Otherwise the client won't connect to the server"
	python client.py --config $< --requests $(firstword $(shell ls -t workdir/*.csv))

