__author__ = 'vikash'

import os.path

from django import template

FMT = 'JPEG'
EXT = 'jpg'
QUAL = 75

register = template.Library()


def resized_path(path, size, method):
    "Returns the path for the resized image."

    dir, name = os.path.split(path)
    image_name, ext = name.rsplit('.', 1)
    return os.path.join(dir, '%s_%s_%s.%s' % (image_name, method, size, EXT))


def scale(imagefield, size, method='scale'):
    """
    Template filter used to scale an image
    that will fit inside the defined area.

    Returns the url of the resized image.

    {% load image_tags %}
    {{ profile.picture|scale:"48x48" }}
    """

    # imagefield can be a dict with "path" and "url" keys
    if imagefield.__class__.__name__ == 'dict':
        imagefield = type('imageobj', (object,), imagefield)

    image_path = resized_path(imagefield.path, size, method)

    if not os.path.exists(image_path):
        try:
            import Image
        except ImportError:
            try:
                from PIL import Image
            except ImportError:
                raise ImportError('Cannot import the Python Image Library.')

        image = Image.open(imagefield.path)


        # normalize image mode
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # parse size string 'WIDTHxHEIGHT'
        width, height = [int(i) for i in size.split('x')]

        # use PIL methods to edit images
        if method == 'scale':
            image.thumbnail((width, height), Image.ANTIALIAS)
            image.save(image_path, FMT, quality=QUAL)

        elif method == 'crop':
            try:
                import ImageOps, ExifTags
            except ImportError:
                from PIL import ImageOps, ExifTags

            ImageOps.fit(image, (width, height), Image.ANTIALIAS
                        ).save(image_path, FMT, quality=QUAL)

    	    try :
                for orientation in ExifTags.TAGS.keys() : 
                    if ExifTags.TAGS[orientation]=='Orientation' : break 
                exif=dict(image._getexif().items())

        	if  exif[orientation] == 3: 
            	    image=image.rotate(180, expand=True)
        	elif exif[orientation] == 6: 
            	    image=image.rotate(270, expand=True)
        	elif exif[orientation] == 8: 
            	    image=image.rotate(90, expand=True)

        	image.save(image_path, FMT, quality=QUAL)

            except ImportError:
                raise ImportError('Cannot rotate.')
			
    return resized_path(imagefield.url, size, method)

def scaleByWidth(imagefield, size, method='scale'):
    """
    Template filter used to scale an image
    that will fit inside the defined area.

    Returns the url of the resized image.

    {% load image_tags %}
    {{ profile.picture|scale:"48x48" }}
    """

    # imagefield can be a dict with "path" and "url" keys
    if imagefield.__class__.__name__ == 'dict':
        imagefield = type('imageobj', (object,), imagefield)

    image_path = resized_path(imagefield.path, size, method)

    if not os.path.exists(image_path):
        try:
            import Image
        except ImportError:
            try:
                from PIL import Image
            except ImportError:
                raise ImportError('Cannot import the Python Image Library.')

        image = Image.open(imagefield.path)

        # normalize image mode
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # parse size string 'WIDTHxHEIGHT'
        # width, height = [int(i) for i in size.split('x')]
        width = int(size)
        wpercent =(width / float(image.size[0]))
        height = int((float(image.size[1]) * float(wpercent)))

        # use PIL methods to edit images
        if method == 'scale':
            image.thumbnail((width, height), Image.ANTIALIAS)
            image.save(image_path, FMT, quality=QUAL)

        elif method == 'crop':
            try:
                import ImageOps
            except ImportError:
                from PIL import ImageOps

            ImageOps.fit(image, (width, height), Image.ANTIALIAS
                        ).save(image_path, FMT, quality=QUAL)

    return resized_path(imagefield.url, size, method)


def crop(imagefield, size):
    """
    Template filter used to crop an image
    to make it fill the defined area.

    {% load image_tags %}
    {{ profile.picture|crop:"48x48" }}

    """
    return scale(imagefield, size, 'crop')

def cropWidth(imagefield, size):
    """
    Template filter used to crop an image
    to make it fill the defined area.

    {% load image_tags %}
    {{ profile.picture|crop:"48x48" }}

    """
    return scaleByWidth(imagefield, size, 'crop')

register.filter('scale', scale)
register.filter('crop', crop)
register.filter('cropWidth', cropWidth)
