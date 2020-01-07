# Python Modules
import os
import argparse
from unittest import TestLoader, TextTestRunner

# mysys Modules
from mysys.dockerize import Docker

from mysys.logger import Logger

if __name__ == '__main__':
    name = "myelkstack"
    logger = Logger(__name__)
    logger.info("{}: Start run container...".format(name))
    parser = argparse.ArgumentParser()

    # define options
    parser.add_argument("-t", "--test", nargs='*', required=False, default=None)
    parser.add_argument("--config", default=None)
    parser.add_argument("--clean", action='store_true', default=False)
    parser.add_argument("--run", action='store_true', default=False)
    parser.add_argument("--reset", action='store_true', default=False)
    
    # parse options
    args = parser.parse_args()
    logger.debug("{}: args is {}".format(name, args))    
    
    if args.test is not None:
        # test myelkstack option
        
        logger.info("{}: Run test..".format(name))
        test_args_count = len(args.test)
        logger.info("{}: test_args_count is {}".format(name, test_args_count))
        # get package & tests path
        pkg_path = os.path.dirname(os.path.abspath(__file__))
        logger.debug("{}: mysys package path is {}".format(name, pkg_path))
        test_path = os.path.join(pkg_path, 'tests')
        logger.info("{}: test_path is {}".format(name, test_path))
        if test_args_count == 0:
            test_pattern = '*_test.py'
        else:
            test_pattern = '{}_test.py'.format(args.test[0])
        
        logger.info("{}: discover test pattern is {}".format(name, test_pattern))
            
        test_loader = TestLoader()
        suite = test_loader.discover(test_path, pattern=test_pattern)
        logger.debug("{}: suite is {}".format(name, suite))
        logger.debug("{}: type(suite) is {}".format(name, suite))
        runner = TextTestRunner()
        result = runner.run(suite)
        logger.debug("{}: test result is {}".format(name, result))

    else:
        # run mysys option
        logger.info("{}: args is {}".format(name, args))
        reset_flag = args.reset
        logger.info("{}: reset_flag is {}".format(name, reset_flag))
        if args.config:
            config_path = os.path.abspath(args.config)
            logger.info("{}: config_path is {}".format(name, config_path))
            if not os.path.isdir(config_path):
                raise ValueError("ConfigPathError: path is not found, config path value is {}.".format(args.config))
            
            docker_client = Docker(config_path, did=True)
            if args.clean:
                logger.info("{}: Clean..".format(name))
                docker_client.clean()
                
            if args.run:
                docker_client.run(reset=reset_flag)
        else:
            raise ValueError("ConfigError: no config value, config path value is {}.".format(args.config))
