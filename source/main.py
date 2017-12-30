import logging
import analysis

logger = logging.getLogger('main')
hdlr = logging.FileHandler('../output.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)


def netowrk(edgelist_file):
    """
    choose the respective analysis required
    :param edgelist_file:
    """
    logger.info('## analysing {} network'.format(edgelist_file))
    # analysis.exact_analysis(edgelist_file, 'lscc')
    # analysis.approx_analysis(edgelist_file, 'lscc', 1, True, 1)
    # analysis.approx_analysis(edgelist_file, 'lscc', 2, True, 1)
    # analysis.approx_analysis(edgelist_file, 'lscc', 3)
    logger.info('## analysis done!')


if __name__ == '__main__':
    logger.info('starting project')
    # change to respective edgelist file location
    netowrk('file to respective components edge-list')
