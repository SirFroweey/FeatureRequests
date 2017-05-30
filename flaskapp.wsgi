#!/usr/bin/python
import sys
import logging

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/lib/jenkins/workspace/ureRequests_Pipeline_master-NJ3GBOEH5JNIZT3C2LR534XVJSQM4GGZZOSUUQ56KC2AWA43NVXA/")

from feature_requests.app import app as application
application.secret_key = '123hosvnkjdhfn2h9023u12093jlkasd11'
