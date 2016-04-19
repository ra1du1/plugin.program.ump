from os import path
from xml.dom import minidom

from xbmcgui import Dialog
from defs import kodi_setxml


logs={
"0":"Buffer all internet filesystems (like 2 but additionally also ftp, webdav, etc.) (default)",
"1":"Buffer all filesystems, both internet and local",
"2":"Only buffer true internet filesystems (streams) (http, etc.)",
"3":"No buffer"
}

setxml=kodi_setxml

def addchild(res,parent,child):
	newnode = res.createElement(child)
	parent.appendChild(newnode)
	return newnode

def getchild(res,parent,child):
	found=False
	for ch in parent.childNodes:
		try:
			if ch.tagName==child:
				return ch
		except:
			continue
	if not found:
		return addchild(res,parent,child)

def force(mode):
	mode=str(mode)
	if path.exists(setxml):
		res=minidom.parse(setxml)
		adv=getchild(res,res,"advancedsettings")
		nw=getchild(res,adv,"network")
		bm=getchild(res,nw,"buffermode")
		for text in bm.childNodes:
			bm.removeChild(text)
		bm.appendChild(res.createTextNode(mode))
	else:
		res=minidom.parseString("<advancedsettings><network><buffermode>%s</buffermode></network></advancedsettings>"%mode)
	res.writexml( open(setxml, 'w'),encoding="UTF-8")
	dialog = Dialog()
	dialog.ok('UMP', 'LibCurl Buffering Mode set to %s'%mode,logs[mode],"YOU NEED TO RESTART KODI TO CHANGES TAKE AFFECT")
	res.unlink()

def get():
	if path.exists(setxml):
		res=minidom.parse(setxml)
		adv=getchild(res,res,"advancedsettings")
		nw=getchild(res,adv,"network")
		bm=getchild(res,nw,"buffermode")
		ret=bm.lastChild.data
		res.unlink()
	else:
		ret="0"
	return ret