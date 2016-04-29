from lxml import html
import requests
import urllib
import os
import codecs
import re
from graphviz import Digraph
from collections import defaultdict
from markdown import markdown,markdownFromFile
import pdfkit

PFAM_STRING = 'Pfam'
REPORT_TEMPLATE_DIR = '{0}/templates'.format(os.path.dirname(os.path.realpath(__file__)))
REPORT_TEMPLATE_FN = '{0}/ReportTemplate.html'.format(REPORT_TEMPLATE_DIR)
REPORT_TEMPLATE_VIS_DIR = '{0}/vis'.format(REPORT_TEMPLATE_DIR)
FUSION_INTRCN_RESULTS_FN = '{0}/../data/output/FIInteractFusionEvents.txt'.format(
    os.path.dirname(os.path.realpath(__file__)))
INTERACTOME_DETAIL_CAPTURE = '^F\s(?P<fusion1>[a-zA-Z0-9]+)-(?P<fusion2>[a-z-A-Z0-9]+),I\s(?P<intrcn1>[a-z-A-Z0-9]+)-(?P<intrcn2>[a-z-A-Z0-9]+),(?P<gene1>[a-zA-Z0-9]+),(?P<gene1uni>[a-zA-Z0-9]+),.+,(?P<gene2>[a-zA-Z0-9]+),(?P<gene2uni>[a-zA-Z0-9]+),.+,Interaction.+'
FUSION_INTRCN_ONLY_CAPTURE = '^F\s(?P<fusion>[a-zA-Z0-9]+-[a-z-A-Z0-9]+),I\s(?P<intrcn>[a-z-A-Z0-9]+-[a-z-A-Z0-9]+),.+'
PNG_DIR = '{0}/../data/output/vis/png'.format(os.path.dirname(os.path.realpath(__file__)))

# Parse Input
f_i_dict = dict()
rep_i_set = set()

if os.path.isfile(FUSION_INTRCN_RESULTS_FN):
    print('reading {0}...'.format(FUSION_INTRCN_RESULTS_FN))
    in_fptr = open(FUSION_INTRCN_RESULTS_FN)
    while 1:
        line = in_fptr.readline()
        if not line:
            break
        match = re.match(FUSION_INTRCN_ONLY_CAPTURE, line)
        if match:
            f = match.group('fusion')
            i = match.group('intrcn')
            print('adding {0} to {1}...'.format(i,f))
            f_i_dict[f] = f_i_dict[f] + [i] if f_i_dict.get(f) is not None else [i]
        match = re.match(INTERACTOME_DETAIL_CAPTURE, line)
        if match:
            print('interaction report generated for {0}'.format(i))
            rep_i_set.add(i)

    # close file
    in_fptr.close()

    # Generate Fusion-Interaction Mapping Image
    dot = Digraph(comment='Fusion-Interaction Mapping')

    # Nodes
    for fusion, intrcn_list in f_i_dict.items():
        print('fusion: {0}'.format(fusion))
        print('intrcn_list: {0}'.format(intrcn_list))
        dot.node(fusion,fusion,style='filled',fillcolor='red')
        for intrcn in intrcn_list:
            print('intrcn: {0}'.format(intrcn))
            if intrcn in rep_i_set:
                dot.node(intrcn,intrcn,shape='box',style='filled',fillcolor='yellow',color='cyan')
            else:
                dot.node(intrcn,intrcn,style='filled',fillcolor='gray')
            # Edges
            dot.edge(fusion,intrcn)

    dot.format = 'png'
    fusion_intrcn_mapping_png_path = '{0}/fusion_intrcn_mapping'.format(PNG_DIR)
    dot.render(fusion_intrcn_mapping_png_path,view=False)
    fusion_intrcn_mapping_png_path = '{0}.png'.format(fusion_intrcn_mapping_png_path)

    print('fusion-interaction mapping image has been written to {0}.'.format(fusion_intrcn_mapping_png_path))