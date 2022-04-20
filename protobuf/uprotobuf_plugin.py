#!/usr/bin/env python3
import os.path as osp
from struct import pack
from sys import prefix
from types import prepare_class
from google.protobuf.compiler import plugin_pb2 as plugin
from google.protobuf.descriptor_pb2 import DescriptorProto, EnumDescriptorProto, FieldDescriptorProto as FProto


def getType(field_type):
    if field_type == FProto.TYPE_BOOL: type = "Bool"
    elif field_type == FProto.TYPE_BYTES: type = "Bytes"
    elif field_type == FProto.TYPE_DOUBLE: type = "Double"
    elif field_type == FProto.TYPE_ENUM: type = "Enum"
    elif field_type == FProto.TYPE_FIXED32: type = "Fixed32"
    elif field_type == FProto.TYPE_FIXED64: type = "Fixed64"
    elif field_type == FProto.TYPE_FLOAT: type = "Float"
    elif field_type == FProto.TYPE_GROUP: type = "Group"
    elif field_type == FProto.TYPE_INT32: type = "Int32"
    elif field_type == FProto.TYPE_INT64: type = "Int64"
    elif field_type == FProto.TYPE_MESSAGE: type = "Message"
    elif field_type == FProto.TYPE_SFIXED32: type = "SignedFixed32"
    elif field_type == FProto.TYPE_SFIXED64: type = "SignedFixed64"
    elif field_type == FProto.TYPE_SINT32: type = "SInt32"
    elif field_type == FProto.TYPE_SINT64: type = "SInt64"
    elif field_type == FProto.TYPE_STRING: type = "String"
    elif field_type == FProto.TYPE_UINT32: type = "UInt32"
    elif field_type == FProto.TYPE_UINT64: type = "UInt64"
    else: raise Exception()
    return type

def message_class(package, item, indent=0):
    prefix = package + "." + item.name
    out = indent * "\t" + "class {}(Message):\n".format(item.name)
    for nested in item.nested_type:
        out += message_class(prefix, nested, indent + 1)
        out += "\n"

    for enum in item.enum_type:
        out += indent * "\t" + "\tclass {}(Enum):\n".format(enum.name)
        for value in enum.value:
            out += (indent + 1) * '\t' + '\t{} = {}\n'.format(value.name, value.number)
        out += "\n"

    out += indent * "\t" + "\t_fields=[\n"

    for field in item.field:
        type_ = getType(field.type)

        out += indent * "\t" +"\t\tField(name='{}', type='{}', id={}".format(
            field.name,
            type_,
            field.number,
        )
        if field.type == FProto.TYPE_ENUM: 
            enum_name = field.type_name.removeprefix(package + ".").removeprefix(item.name + ".")
            out += ", cls={}".format(enum_name)

        if field.label == FProto.LABEL_REQUIRED:
            out += ", required=True"
        elif field.label == FProto.LABEL_REPEATED:
            out += ", repeated=True"

        if field.type == FProto.TYPE_MESSAGE:
            field_name = field.type_name.removeprefix(package + ".").removeprefix(item.name + ".")
            out += ", cls={}".format(field_name)
        out += "),\n"
    out += indent * "\t" +"\t]\n"

    return out.expandtabs(4)

    
def generateCode(request, response):
    for proto_file in request.proto_file:
        output = '"""ATTENTION! This module is autogenerated! Don\'t edit!"""\n\n'
        output += "from protobuf.uprotobuf import Message, Field, Enum\n\n"
        output += "PACKAGE='{}'\n\n".format(proto_file.package)

        for item in proto_file.message_type:
            print((item, type(item)), file=open('item.out', 'a'))
            if isinstance(item, DescriptorProto):
                output += message_class("." + proto_file.package, item)

        f = response.file.add()
        f.name = "{}_upb2.py".format(osp.splitext(proto_file.name)[0])
        f.content = output 

if __name__ == "__main__":
    from sys import stdin, stdout

    data = stdin.buffer.read()
    request = plugin.CodeGeneratorRequest()
    request.ParseFromString(data)
    response = plugin.CodeGeneratorResponse()
    generateCode(request, response)
    output = response.SerializeToString()
    stdout.buffer.write(output)