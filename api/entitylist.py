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
    parser.add_argument('where',type=str, help='Valid sql where clause', location='query')
    parser.add_argument('orderby',type=str, help='Valid sql orderby clause', location='query')
    parser.add_argument('select',type=str, help='Valid sql select', location='query')
    parser.add_argument('pagesize', type=int, help='Pagesize of the resultset',default=5000, location='query')
    parser.add_argument('page', type=int, help='Page',default=1, location='query')
    return parser


class EntityList(Resource):
    api=AppInfo.get_api()
    @api.doc(parser=create_parser())
    def get(self, table):
        parser=create_parser().parse_args()
        context=g.context

        if request.json==None:
            abort(400, "No cannot extract json data in body %s %s" % (table,id))

        query=build_fetchxml_by_alias(context,table,id, request.json)
        builder=factory.create_command('select', query=query)
        rs=DatabaseServices.exec(builder,context,fetch_mode=0)
        result={"rows_affected": rs.get_cursor().rowcount}

        return result



def get_endpoint():
    return EntityList
