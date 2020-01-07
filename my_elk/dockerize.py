# Python Module
import os
import json
import time

# External Module
from jsonschema import validate
import docker 
from docker.errors import ImageNotFound # image not found
from docker.errors import NotFound

from mysys.logger import Logger

from mysys import Schema
from mysys import config_schemas

class Docker:
    PULL_CONFIG_FILENAME = "pull_config.json"
    BUILD_CONFIG_FILENAME = "build_config.json"
    RUN_CONFIG_FILENAME = "run_config.json"
    
    def __init__(self, config, did=False, run_config_filename=None, build_config_filename=None, pull_config_filename=None, logger=None, log_file=None, *args, **kwargs):
        if logger is None:
            self.logger = Logger("Docker", log_file=log_file)
        else:
            self.logger = logger
        
        if config is None:
            self.logger.info("no config path")
            raise ValueError("Docker: no config path.")
        # self.config_path = config
        self.did = did

        if run_config_filename is None:
            run_config_filename = self.RUN_CONFIG_FILENAME
        self.logger.info(run_config_filename)

        if build_config_filename is None: 
            build_config_filename = self.BUILD_CONFIG_FILENAME 
        self.logger.info(build_config_filename)

        if pull_config_filename is None: 
            pull_config_filename = self.PULL_CONFIG_FILENAME
        self.logger.info(pull_config_filename)

        self.load_configs(config, run_config_filename=run_config_filename, build_config_filename=build_config_filename, pull_config_filename=pull_config_filename)
        
        self.docker_host = os.environ['DOCKER_HOST']
        self.name = os.environ.get('CONTAINER_NAME', None)
        if self.name is None:
            raise ValueError("Docker: None-existance of the container name")

        self.docker = docker.DockerClient(base_url=self.docker_host)
        self.low_docker = docker.APIClient(base_url=self.docker_host)

        # get host path
        # /code/config
        # /ddddd///:/code
        if self.did:
            container = self.docker.containers.get(self.name)
            binds = container.attrs['HostConfig']['Binds']
            for bind in binds:
                if ':/code' in bind:
                    splited_bind = bind.split(':')
                    self.config_path = splited_bind[0] + config.replace(splited_bind[1], '')
                    self.logger.info(self.config_path)

    def load_configs(self, config, run_config_filename=None, build_config_filename=None, pull_config_filename=None):
        run_config_path = os.path.join(config, run_config_filename)
        build_config_path = os.path.join(config, build_config_filename)
        pull_config_path = os.path.join(config, pull_config_filename)
        
        # validate path
        config_count = 0
        self.logger.debug(os.listdir(os.path.dirname(run_config_path)))
        if os.path.isfile(run_config_path):
            self.logger.debug(run_config_path)
            with open(run_config_path) as run_config_file:
                self.run_config = json.load(run_config_file)
            # validate run config
            # empty check
            if self.run_config:
                validate(instance=self.run_config, schema=config_schemas[Schema.RUN])
                config_count += 1
        else:
            raise ValueError("Docker: ConfigPathError: run config path is not found, run config path is {}.".format(run_config_path))
        if os.path.isfile(build_config_path):
            self.logger.debug(build_config_path)
            with open(build_config_path) as build_config_file:
                self.build_config = json.load(build_config_file)
            # validate build config
            # empty check
            if self.build_config:
                validate(instance=self.build_config, schema=config_schemas[Schema.BUILD])
                config_count += 1
        else:
            raise ValueError("Docker: ConfigPathError: build config path is not found, build config path is {}.".format(build_config_path))

        if os.path.isfile(pull_config_path):
            self.logger.info(pull_config_path)
            with open(pull_config_path) as pull_config_file:
                self.pull_config = json.load(pull_config_file)
            # validate pull config
            # empty check
            if self.pull_config:
                validate(instance=self.pull_config, schema=config_schemas[Schema.PULL])
                config_count += 1
            self.logger.debug(config_count)
            if config_count == 0:
                raise ValueError("Docker: ConfigError: no config")
        else:
            raise ValueError("Docker: ConfigPathError: pull config path is not found, pull config path is {}.".format(pull_config_path))

    def pull(self):
        self.logger.info(self.pull_config)
        for config in self.pull_config:
            repository = config.get('repository')
            tag = config.get('tag')
            image_name = "{}:{}".format(repository, tag)
            try:
                self.docker.images.get(image_name)
            except NotFound as Error:
                self.logger.info("pull image")
                self.logger.info(Error)
                self.docker.images.pull(*(config.values()))

    def build(self):
        self.logger.info(self.build_config)
        for config in self.build_config:
            image_name = config.get('tag')
            try:
                self.docker.images.get(image_name)
                # image = self.docker.images.get(image_name)
            except NotFound as Error:
                self.logger.info("build image")
                self.logger.info(Error)
                self.docker.images.build(**config)

    def _run(self):
        for config in self.run_config:
            self.logger.info("Docker: The current config is {}".format(config))
            image_name = config.get('image')
            try:
                self.docker.images.get(image_name)
            except NotFound as Error:
                self.logger.info("Docker: Non-existance of the image whose name is {}".format(image_name))
                self.logger.info(Error)
                found_image = False
                # find image build config
                for c in self.build_config:
                    build_image_name = c.get('tag')
                    if image_name == build_image_name:
                        found_image = True
                        self.docker.images.build(**c)
                        break
                if not found_image:
                    # find image pull config
                    for c in self.pull_config:
                        repository = c.get('repository')
                        tag = c.get('tag')
                        pull_image_name = "{}:{}".format(repository, tag)
                        if image_name == pull_image_name:
                            self.docker.images.pull(**c)
                            break

            self.logger.info("Docker: config path is {}".format(self.config_path))
            # self.logger.info("Docker: self.did is {}".format(self.did))
            # self.logger.info("Docker: self.did is True is {}".format(self.did is True))
            # self.logger.info("Docker: config is {}".format(config))
            if self.did is True:
                if 'volumes' in config:
                    volumes = {}
                    for key, value in config['volumes'].items():

                        if '/var' not in key:
                            self.logger.info("Docker: /var not in key path")
                            self.logger.info("key: {}".format(key))
                            self.logger.info("value: {}".format(value))
                            
                            volumes[self.config_path+'/'+key] = value
                        else:
                            volumes[key] = value
                    config['volumes'] = volumes

                self.logger.info("Docker: after updated, config is {}".format(config))

            # if 'volumes' in config:
            #     if self.did is True:
            #         volumes = {}
            #         self.logger.info(self.host_path)
            #         for key, value in config['volumes'].items():
            #             if '/var' not in key:
            #                 volumes[self.host_path+'/'+key] = value
            #             else:
            #                 volumes[key] = value
            #         config['volumes'] = volumes
            #         self.logger.info(config['volumes'])

            if 'network' in config:
                network_name = config['network']
                try:
                    try:
                        network = self.docker.networks.get(network_name)
                    except NotFound as Error:
                        self.logger.info("Non-existance of the network whose name is {}".format(network_name))
                        self.logger.info(Error)
                        self.docker.networks.create(network_name)
                except Exception as Error:
                    self.logger.error("Error is occured in creating network")
                    self.logger.error(config)
                    self.logger.error(Error)
                    raise Error
            try:
                container_name = config['name']
                try:
                    container = self.docker.containers.get(container_name)
                    if container.status == 'exited':
                        container.remove()
                        self.docker.containers.run(**config)
                except NotFound as Error:
                    self.logger.info("Non-existance of the container whose name is {}".format(container_name))
                    self.logger.info(Error)
                    self.docker.containers.run(**config)
            except Exception as Error:
                self.logger.error("Error is occured in running container")
                self.logger.error(config)
                self.logger.error(Error)
                raise Error

    def run(self, reset=False):
        # [   ] myelasticstack
        # [   ]     mymonitor-elasticsearch
        # [   ]     mymonitor-kibana
        # [   ]     mymonitor-logstash

        self.logger.info("reset value is {}".format(reset))
        if reset:
            self.clean()
        # self.pull()
        # self.build()
        self._run()

    def stop(self):
        for config in self.run_config:
            container_name = config['name']
            try:
                container = self.docker.containers.get(container_name)
            except NotFound as Error:
                self.logger.info("Non-existance of the container whose name is {}".format(container_name))
                self.logger.info(config)
                self.logger.info(Error)
            self.logger.info(container.status)
            try:
                container.stop()
            except Exception as Error:
                self.logger.error(Error)
                raise Error

    def clean(self):
        # stop & remove containers
        for config in self.run_config:
            container_name = config['name']
            try:
                container = self.docker.containers.get(container_name)
                self.logger.info(container.status)
                try:
                    if container.status == 'exited':
                        container.remove()
                    else:
                        container.stop()
                        container.remove()
                except Exception as Error:
                    self.logger.error(Error)
                    raise Error
            except NotFound as Error:
                self.logger.info("Non-existance of the container whose name is {}".format(container_name))
                self.logger.info(config)
                self.logger.info(Error)
        # remove images
        # remove pulled images
        for config in self.pull_config:
            repository = config.get('repository')
            tag = config.get('tag')
            image_name = "{}:{}".format(repository, tag)
            try:
                self.docker.images.remove(image_name)
            except Exception as Error:
                self.logger.info(Error)
        # remove build images
        for config in self.build_config:
            image_name = config.get('tag')
            try:
                self.docker.images.remove(image_name)
            except Exception as Error:
                self.logger.info(Error)

    def remove_container(self):
        pass

    def remove_images(self):
        pass

if __name__ == '__main__':
    pass
