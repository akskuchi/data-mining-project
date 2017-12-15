import logging
import analysis

logger = logging.getLogger('main')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def wiki_vote_network(edgelist_file):
    analysis.analyse(edgelist_file)


if __name__ == '__main__':
    logger.info('starting project')
    wiki_vote_network('resources/wiki-Vote.txt')
