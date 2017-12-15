import logging
import analysis

logger = logging.getLogger('main')
hdlr = logging.FileHandler('../output.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)


def wiki_vote_network(edgelist_file):
    logger.info('## analysing {} network'.format(edgelist_file))
    analysis.analyse(edgelist_file)
    logger.info('## analysis done!')


if __name__ == '__main__':
    logger.info('starting project')
    wiki_vote_network('resources/wiki-Vote.txt')
