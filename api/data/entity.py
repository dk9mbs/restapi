#!/usr/bin/python3

from flask import Flask, g, session
from flask import abort
from flask import Blueprint
from flask import request
from flask_restplus import Resource, Api, reqparse
from flaskext.mysql import MySQL

from core.appinfo import AppInfo
from core.database import CommandBuilderFactory as factory
from services.fetchxml import build_fetchxml_by_alias
from services.database import DatabaseServices

def create_parser_get():
    parser=reqparse.RequestParser()
    parser.add_argument('select',type=str, help='Valid sql select', location='query')
    return parser

def create_parser_put():
    parser=reqparse.RequestParser()
    return parser

def create_parser_delete():
    parser=reqparse.RequestParser()
    return parser


class Entity(Resource):
    api=AppInfo.get_api()

    @api.doc(parser=create_parser_delete())
    def delete(self,table,id):
        try:
            create_parser_delete().parse_args()
            context=g.context
            fetch=build_fetchxml_by_alias(context,table,id)
            builder=factory.create_command('delete', fetch_xml=fetch)
            rs=DatabaseServices.exec(builder,context, fetch_mode=0)
            result={"rows_affected": rs.get_cursor().rowcount}
            rs.close()
            return result
        except NameError as err:
            abort(400, f"{err}")


    @api.doc(parser=create_parser_put())
    def put(self,table,id):
        try:
            create_parser_put().parse_args()
            context=g.context

            if request.json==None:
                abort(400, "cannot extract json data in body %s %s" % (table,id))

            fetch=build_fetchxml_by_alias(context, table, id, request.json)
            builder=factory.create_command('update', fetch_xml=fetch)
            rs=DatabaseServices.exec(builder,context, fetch_mode=0)
            result={"rows_affected": rs.get_cursor().rowcount}
            rs.close()
            return result
        except NameError  as err:
            abort(400, f"{err}")
        #except pymysql.err.IntegrityError as err:
        #    abort(400, f"{err}")


    @api.doc(parser=create_parser_get())
    def get(self,table,id):
        try:
            create_parser_get().parse_args()
            context=g.context

            fetch=build_fetchxml_by_alias(context, table, id)

            builder=factory.create_command('select',fetch_xml=fetch)
            rs=DatabaseServices.exec(builder,context, fetch_mode=1)

            if rs.get_result()==None:
                abort(400, "Item not found => %s" % id)

            return rs.get_result()
        except NameError as err:
            abort(400, f"{err}")

def get_endpoint():
    return Entity
