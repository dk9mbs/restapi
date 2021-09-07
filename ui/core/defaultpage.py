#!/usr/bin/python3

import sys
from flask import Flask, g, session, redirect, abort,request,Blueprint
from flask import make_response
from flask_restplus import Resource, Api, reqparse
from core.appinfo import AppInfo
from core import log

logger=log.create_logger(__name__)

def create_parser():
    parser=reqparse.RequestParser()
    return parser

class DefaultPage(Resource):
    api=AppInfo.get_api("content")

    @api.doc(parser=create_parser())
    def get(self):
        try:
            logger.info(f"redirect to the default page index.htm")

            create_parser().parse_args()
            context=g.context


            return redirect(f"/index.htm", code=302)

        except Exception as err:
            logger.info(f"Exception: {err}")
            abort(500,f"{err}")

def get_endpoint():
    return DefaultPage
