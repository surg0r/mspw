# Create a bitcoin multisignature paper wallet with variable m-of-n settings..
from bitcoin import *
from qrcode import *
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import textwrap

#return a qrcode img for a bitcoin address
def qrc(address):
    qr = QRCode(box_size=3, border=3,error_correction=ERROR_CORRECT_Q)
    qr.add_data(address)
    qrim = qr.make_image()
    qrim_w, qrim_h = qrim.size
    return qrim, qrim_h, qrim_w

#paint the image with qrcode and text for address assumes image open..img.
def addr2img(y, address, x):
    qrim, qrim_h, qrim_w = qrc(address)             #paste qr code to the img at offset based on n..
    offset=(((x-qrim_w)-10),y)
    img.paste(qrim,offset)
    draw.text((0,y), address, (255,255,255),font)    #paste address at level of qr..
    return y+qrim_h

print '>>> Multi-signature paper wallet creator <<<'
print 'How many keyholders for the multisignature address(n)?'
nkeys = int(raw_input())
if nkeys > 12:
    print 'n cannot be greater than 12'
    exit()
#need error for no number input..or if only one key
print 'How many keys required to spend funds at the address(m)?'
mkeys = int(raw_input())
if mkeys > nkeys:
    print 'm cannot be greater than n'
    exit()

print 'How many of', nkeys, 'private keys do you wish to generate randomly now? (must be',nkeys, 'or below, enter for all freshly generated keys)'
rankeys = raw_input()
if not rankeys:
    rankeys = nkeys
rankeys = int(rankeys)

priv = []
wif = []
pub = []

if rankeys > 0:
    print '>>>Generating', rankeys, 'random keys..'
    for x in range(0,rankeys):
        priv.append(random_key())

if nkeys-rankeys > 0:
    print 'Please supply', nkeys-rankeys, 'private keys..(paste a key then hit enter)'
    for x in range(0,(nkeys-rankeys)):
        print 'Paste private key number', x+1
        priv.append(raw_input())    #add error checking for bitcoin address

for x in range(0,nkeys):
    wif.append(encode_privkey(priv[x],'wif'))
    pub.append(privtopub(priv[x]))

print '>>>Creating a multi sig transaction (m-of-n):', mkeys, 'of', nkeys
script = mk_multisig_script(pub, mkeys, nkeys)
addr_multi = scriptaddr(script)

print '>>>multisig bitcoin receiving address:', addr_multi
print '>>>private keys:  '
for x in range(len(priv)):
    print x+1, priv[x]
    print pub[x]
print '>>>multisignature script:', script
print '>>>Creating paper wallet image file..'

im, im_h, im_w = qrc(addr_multi)
tot_h = 0
img_w = 1024
#calculate image height requirements based upon QR code heights.. nkeys * (qrcode[0-x+10]
for x in range(0,nkeys):
    check_im, check_im_h, check_im_w = qrc(priv[x])
    tot_h = tot_h + check_im_h
print tot_h
lines = textwrap.wrap(script,width=70)
offs=(len(lines)*22)+66+10
tot_h=offs + tot_h
print offs, tot_h

img = Image.new( 'RGB', (1024,tot_h), "black")
img_w, img_h = img.size
font = ImageFont.truetype("Arial Bold.ttf",22)
draw = ImageDraw.Draw(img)

im, im_h, im_w = qrc(addr_multi)
offset = (((img_w-im_w)-10), 0)

bg = Image.open("bg.jpg")
bg_w, bg_h = bg.size
img.paste(bg, (0,0))
if tot_h > bg_h:
    img.paste(bg,(0,bg_h))

img.paste(im, offset)

draw.text((0, 0), 'Multisig paper wallet ' + str(mkeys) + ' - of - ' + str(nkeys) + ':', (255,255,255),font)
draw.text((0, 22), 'Multisig address: '+addr_multi, (255,255,255),font)
draw.text((0,44), 'Multisig payment script:', (255,255,255),font)
y=66
for line in lines:
    draw.text((0,y),line,(255,255,255),font)
    y+=22

for x in range(0,nkeys):
    offs1=addr2img(offs,wif[x],img_w)
    offs=offs1+10

img.save('mspw-QR.jpg')