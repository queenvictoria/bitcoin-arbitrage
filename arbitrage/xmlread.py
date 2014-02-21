"""
@author: Jason Chan <bearish_trader@yahoo.com>

BTC:  1ZAWfGTTyv1HuqJemnDsdQChCpiAAaZYZ
QRK:  QQcy1tMSdK8afj1gckxKJs86izP7emEitP
DOGE: DEdHx4GSjawoiSjbjWwr4BKH9Njx235CeH
MAX:  mf93aDHYqk5MxfAFvMXk8Cn1fQW6S37GYQ
MTC:  miCSJ57pae6XWi3knkmSUZXfHHg3bEEpLe
PRT:  PYdxGCTSc2tGvRbpQjwZpnktbzRqvU4DYR
DTC:  DRTJnJ9CW4WUqhPecfhRahC3SoCgXbQcN4

Borrowed the original code from http://code.activestate.com/recipes/116539/
and wrapped it in Xml2Dict class plus added specialized handling for the
McxNow order book
"""
from xml.dom.minidom import parseString

class NotTextNodeError(Exception):
    pass

class Xml2Dict:
    def __init__(self):
        self.name = self.name = self.__class__.__name__

    def getTextFromNode(self, node):
        """
        scans through all children of node and gathers the
        text. if node has non-text child-nodes, then
        NotTextNodeError is raised.
        """
        t = ""
        for n in node.childNodes:
            if n.nodeType == n.TEXT_NODE:
                t += n.nodeValue
            else:
                raise NotTextNodeError
        return t

    def nodeToDic(self, node):
        """
        nodeToDic() scans through the children of node and makes a
        dictionary from the content.
        three cases are differentiated:
        - if the node contains no other nodes, it is a text-node
        and {nodeName:text} is merged into the dictionary.
        - if the node has the attribute "method" set to "true",
        then it's children will be appended to a list and this
        list is merged to the dictionary in the form: {nodeName:list}.
        - else, nodeToDic() will call itself recursively on
        the nodes children (merging {nodeName:nodeToDic()} to
        the dictionary).
        """
        dic = {} 
        for n in node.childNodes:
            if n.nodeType != n.ELEMENT_NODE:
                continue
            if n.nodeName in ("buy", "sell", "rich", "history", "vol", "tabprice"):
            # node with multiple children:
            # put them in a list
                l = []
                for c in n.childNodes:
                    if c.nodeType != n.ELEMENT_NODE:
                        continue
                    d = self.nodeToDic(c)
                    if d:
                        l.append(d)
                    dic.update({n.nodeName:l})
                continue
        
            try:
                text = self.getTextFromNode(n)
            except NotTextNodeError:
                # 'normal' node
                dic.update({n.nodeName:self.nodeToDic(n)})
                continue
            
            # text node
            dic.update({n.nodeName:text})
            continue
        return dic

    def getDictFromXml(self,xmlstr):
        dom = parseString(xmlstr)
        return self.nodeToDic(dom)

def test():
    xml2dict = Xml2Dict()
    dic = xml2dict.getDictFromXml( #Sample XML for test
    '<?xml version="1.0" encoding="UTF-8"?>\
    <Config><Name>My Config File</Name>\
    <Items multiple="true">\
        <Item><Name>First Item</Name>\
        <Value>Value 1</Value>\
    </Item>\
    <Item>\
        <Name>Second Item</Name>\
        <Value>Value 2</Value>\
    </Item>\
    </Items>\
    </Config>')
    print(dic["Config"]["Name"])
    print()
    for item in dic["Config"]["Items"]:
        print("Item's Name:", item["Name"])
        print("Item's Value:", item["Value"])

if __name__ == "__main__":
    test()
#
#==================================================
#sample.xml:
#==================================================
#<?xml version="1.0" encoding="UTF-8"?>
#
#<Config>
#    <Name>My Config File</Name>
#    
#    <Items multiple="true">
#    <Item>
#        <Name>First Item</Name>
#        <Value>Value 1</Value>
#    </Item>
#    <Item>
#        <Name>Second Item</Name>
#        <Value>Value 2</Value>
#    </Item>
#    </Items>
#
#</Config>
#
#
#
#==================================================
#output:
#==================================================
#My Config File
#
#Item's Name: First Item
#Item's Value: Value 1
#Item's Name: Second Item
#Item's Value: Value 2