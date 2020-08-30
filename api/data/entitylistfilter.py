#!/usr/bin/python3

from flask import Flask,request,abort,g ,session
from flask import Blueprint
from flask_restplus import Resource, Api, reqparse
from flaskext.mysql import MySQL

from core.appinfo import AppInfo
from core.database import CommandBuilderFactory as factory
from services.fetchxml import build_fetchxml_by_alias
from services.database import DatabaseServices

def create_parser():
    parser=reqparse.RequestParser()
    return parser


class EntityListFilter(Resource):
    api=AppInfo.get_api()
    @api.doc(parser=create_parser())
    def post(self):
        try:
            parser=create_parser().parse_args()
            context=g.context
            fetch=request.data
            #print(fetch)
            builder=factory.create_command('select', fetch_xml=fetch)
            rs=DatabaseServices.exec(builder,context,fetch_mode=0)
            #print(rs.get_result())
            return rs.get_result()
        except NameError as err:
            abort(400, f"{err}")



def get_endpoint():
    return EntityListFilter
