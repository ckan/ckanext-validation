# encoding: utf-8
import json
import sys

value = sys.stdin.read()
sys.stderr.write(value)
print(json.loads(value)['result']['id'])
