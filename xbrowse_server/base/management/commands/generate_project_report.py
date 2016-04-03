from optparse import make_option
import sys
import os
from django.core.management.base import BaseCommand
from xbrowse_server.reports.utilities import fetch_project_individuals_data
import json
import time
import datetime
#Note: this require pypl tool lib: reportlab (pip install reportlab)

from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch 
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_RIGHT, TA_CENTER, TA_LEFT



class Command(BaseCommand):
    __VERSION__= '0.0.1'

    def add_arguments(self, parser):
        parser.add_argument('args', nargs='*')
        parser.add_argument('--family_id',
                    dest='family_id',
                    help='Generate report for this family only.'
                    )

    def handle(self, *args, **options):
      '''
        Generates a report for a project
      '''
      
      if len(args)==0:
        print '\n\nGenerates a report for a project.\n'
        print 'Please enter project ID'
        print '\n'
        sys.exit()
      project_id=args[0]
      family_data,variant_data = fetch_project_individuals_data(project_id)
      self.gen_pdf(family_data,variant_data,project_id)

      
    def gen_pdf(self,family_data,variant_data,project_id):
      '''
        Generate a PDF report
      '''
      story=[]
      doc = SimpleDocTemplate("test.pdf",
                              pagesize=letter,
                              rightMargin=72,
                              leftMargin=72,
                              topMargin=72,
                              bottomMargin=18)

      #styling
      styles=getSampleStyleSheet()
      styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
      styles.add(ParagraphStyle(name='main_title_text', fontName ='Helvetica',fontSize=18, backColor = colors.white, textColor=colors.black, alignment=TA_LEFT))
      styles.add(ParagraphStyle(name='sub_title_text', fontName ='Helvetica',fontSize=16, backColor = colors.white, textColor=colors.black, alignment=TA_LEFT))
      styles.add(ParagraphStyle(name='section_title_text', fontName ='Helvetica',fontSize=12, backColor = colors.white, textColor=colors.black, alignment=TA_LEFT))
      styles.add(ParagraphStyle(name='regular_text', fontName ='Helvetica',fontSize=9, backColor = colors.white, textColor=colors.black, alignment=TA_LEFT))
      
      #add logo
      i=Image('/Users/harindra/Desktop/logo.png',width=2*inch, height=0.5*inch)
      story.append(i)
      story.append(Spacer(1, 12))
      
       #add main title
      para = 'The Center For Mendelian Genomics'
      story.append(Paragraph(para, styles["main_title_text"])) 
      story.append(Spacer(width=1, height=20))
      
      #add title
      para = 'Project Report for %s' % project_id
      story.append(Paragraph(para, styles["sub_title_text"])) 
      story.append(Spacer(1, 12))
      
      #add time stamp
      t = time.time()
      tstamp = datetime.datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S')
      para = 'Report generated at: %s' % tstamp
      story.append(Paragraph(para, styles["regular_text"])) 
      para = 'Tool version: %s' % self.__VERSION__
      story.append(Paragraph(para, styles["regular_text"])) 
      story.append(Spacer(1, 12))
      
      #Sections
      #--------Causal variants
      para = 'Causal Variants found in project'
      story.append(Paragraph(para, styles["section_title_text"]))       
      story.append(Spacer(1, 12))
      
      for i,fam in enumerate(json.loads(family_data)):
        dets = 'Family ID: %d:' % i
        story.append(Paragraph(dets, styles['regular_text'])) 
        for gene_id,gene_data in fam['extras']['genes'].iteritems():
          dets = '<para leftIndent="2cm">Gene symbol: %s</para>' % gene_data['symbol']
          story.append(Paragraph(dets,styles['regular_text'])) 
      #--------
      
      doc.build(story)
