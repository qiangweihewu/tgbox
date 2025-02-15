Examples
========

Logging in & Box creation
-------------------------

.. code-block:: python

        from tgbox.api import (
            TelegramAccount, 
            make_remote_box,
            make_local_box
        )
        from asyncio import run as asyncio_run
        from tgbox.keys import Phrase, make_basekey
        from getpass import getpass # Hidden input
        
        phone_number = input('Your phone number: ')
        
        # This two will not work. Get your own at https://my.telegram.org 
        API_ID, API_HASH = 1234567, '00000000000000000000000000000000' 

        async def main():
            ta = TelegramAccount(
                phone_number = phone_number,
                api_id = API_ID, 
                api_hash = API_HASH
            )
            await ta.connect() # Connecting with Telegram
            await ta.send_code_request() # Requesting login code

            await ta.sign_in(
                code = int(input('Code: ')),
                password = getpass('Pass: ')
            )
            # Generating your passphrase
            p = Phrase.generate()
            print(p.phrase.decode())
            
            # WARNING: This will use 1GB of RAM for a
            # couple of seconds. See help(make_basekey)
            basekey = make_basekey(p)

            # Make EncryptedRemoteBox
            erb = await make_remote_box(ta)
            # Make DecryptedLocalBox
            dlb = await make_local_box(erb, ta, basekey)
            
            # Close all connections
            # after work was done
            await erb.done()
            await dlb.done()
        
        asyncio_run(main())

File uploading 
--------------

One upload
^^^^^^^^^^

.. code-block:: python
        
        from asyncio import run as asyncio_run
        from tgbox.api import get_local_box, get_remote_box
        from tgbox.keys import Phrase, make_basekey


        async def main():
            # Better to use getpass.getpass, but
            # it's can be hard to input passphrase 
            # without UI. It's just example, so OK.
            p = Phrase(input('Your Passphrase: '))

            # WARNING: This will use 1GB of RAM for a
            # couple of seconds. See help(make_basekey).
            basekey = make_basekey(p)

            # Opening & decrypting LocalBox. You
            # can also specify MainKey instead BaseKey
            dlb = await get_local_box(basekey)

            # Getting DecryptedRemoteBox
            drb = await get_remote_box(dlb)
            
            # CATTRS is a File's CustomAttributes. You
            # can specify any you want. Here we will add
            # a "comment" attr with a true statement :^)
            cattrs = {'comment': b'Cats are cool B-)'}

            # Preparing file for upload. This will return a PreparedFile object
            pf = await dlb.prepare_file(open('cats.png','rb'), cattrs=cattrs)

            # Uploading PreparedFile to the RemoteBox
            # and return DecryptedRemoteBoxFile
            drbf = await drb.push_file(pf)

            # Retrieving some info from the RemoteBoxFile 

            print('File size:', drbf.size, 'bytes')
            print('File name:', drbf.file_name.decode())

            # You can also access all information about
            # the RemoteBoxFile you need from the LocalBox
            dlbf = await dlb.get_file(drb.id)

            print('File path:', dlbf.file_path)
            print('Custom Attributes:', dlbf.cattrs)

            # Downloading file back.
            await drbf.download()
        
        asyncio_run(main())

.. tip::
    Using the *LocalBox* instead of the *RemoteBox* is **always** better. Use LocalBox for accessing information about the Box files. Use RemoteBox for downloading them.

.. note::
    For the next examples let's assume that we already have ``DecryptedLocalBox`` (as ``dlb``) & ``DecryptedRemoteBox`` (as ``drb``) to respect `DRY <https://en.wikipedia.org/wiki/Don%27t_repeat_yourself>`_.

Multi-upload
^^^^^^^^^^^^

.. code-block:: python
        
        from asyncio import gather

        ... # some code was omitted
        
        # This will upload three files concurrently, wait 
        # and return list of DecryptedRemoteBoxFile

        drbf_list = await gather(
            drb.push_file(await dlb.prepare_file(open('cats2.png','rb'))),
            drb.push_file(await dlb.prepare_file(open('cats3.png','rb'))),
            drb.push_file(await dlb.prepare_file(open('cats4.png','rb')))
        )
        for drbf in drbf_list:
            print(drbf.id, drbf.file_name)

.. warning::
    You will receive a 429 (Flood) error and will be restricted for uploading files for some time if you will spam Telegram servers. Vanilla clients allow users to upload 1-3 files per time and no more, however, if you will upload 10 small files at the same time it will be OK, but if you will upload even three big files similarly then you almost guarantee to get a flood error. 


Iterating 
---------

Over files
^^^^^^^^^^

.. code-block:: python
        
        ... # some code was omitted

        # Iterating over files in RemoteBox
        async for drbf in drb.files():
            print(drbf.id, drbf.file_name)

        # Iterating over files in LocalBox
        async for dlbfi in dlb.files():
            print(dlbfi.id, dlbfi.file_name)


Deep local iteration & Directories
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python
        
        ... # some code was omitted
        
        from tgbox.api import DecryptedLocalBoxFile

        # In this example we will iterate over all
        # asbstract LocalBox contents: Files and Directories

        # To iterate for directories only you can set the
        # ignore_files kwarg to True. 

        async for content in dlb.contents(ignore_files=False):
            if isinstance(content, DecryptedLocalBoxFile):
                print('File:', file.id, file.file_name, file.size)
            else:
                await content.lload(full=True) # Load directory path
                print('Dir:', content, content.part_id.hex())

.. note::
    *RemoteBox* doesn't have the ``.contents()`` generator


Download file preview
---------------------

.. code-block:: python
        
    ... # some code was omitted

    # You can also call this methods on DecryptedRemoteBox,
    # but DecryptedLocalBox is recommend and preferable.
    
    # Get a last DecryptedLocalBoxFile from LocalBox
    last_dlbf = await drb.get_file(await dlb.get_last_file_id())

    with open(f'{last_dlbf.file_name}_preview.jpg','wb') as f:
        f.write(last_dlbf.preview)

File search
-----------

.. code-block:: python
        
    ... # some code was omitted
    
    from tgbox.tools import SearchFilter
    
    # With this filter, method will search
    # all image files by mime with a minimum
    # size of 500 kilobytes. 

    # See help(SearchFilter) for more
    # keyword arguments and help.

    sf = SearchFilter(mime='image/', min_size=500000)

    # You can also search on RemoteBox
    async for dlbfi in dlb.search_file(ff):
        print(dlbfi.id, dlbfi.file_name)

Box clone
---------

.. code-block:: python

    from tgbox.api import (
        TelegramAccount,
        get_remote_box
    )

    from tgbox.keys import make_basekey, Key
    from asyncio import run as asyncio_run
    from getpass import getpass

    phone_number = input('Your phone number: ')

    # This two is example. Get your own at https://my.telegram.org 
    API_ID, API_HASH = 1234567, '00000000000000000000000000000000' 

    async def main():
        ta = TelegramAccount(
            phone_number = phone_number,
            api_id = API_ID, 
            api_hash = API_HASH
        )
        await ta.connect() # Connecting with Telegram
        await ta.send_code_request() # Requesting login code

        await ta.sign_in(
            code = int(input('Code: ')),
            password = getpass('Pass: ')
        )
        # Make decryption key for cloned Box.
        # Please, use strength Phrase, we
        # encrypt with it your Telegram session.
        # See keys.Phrase.generate method.
        basekey = make_basekey(b'very bad phrase')

        # Retreive RemoteBox by username (entity),
        # you may also use here invite link.
        # 
        # In this example we will clone created
        # by Non RemoteBox. MainKey of it is
        # already disclosed. NEVER DISCLOSE
        # keys of your private Boxes. If you
        # want to share Box with someone
        # else, use ShareKey. See docs.
        #
        # Retreiving MainKey will give
        # FULL R/O ACCESS to your files.
        erb = await get_remote_box(ta=ta, entity='@nontgbox_non')

        # Disclosed MainKey of the @nontgbox_non
        # RemoteBox. See t.me/nontgbox_non/67
        mainkey = Key.decode(
            'MbxTyN4T2hzq4sb90YSfWB4uFtL03aIJjiITNUyTqdoU='
        )
        # Decrypt @nontgbox_non
        drb = await erb.decrypt(key=mainkey)
        # Clone and retreive DecryptedLocalBox
        dlb = await drb.clone(basekey)

        await dlb.done()
        await drb.done()
    
    asyncio_run(main())

Telethon
--------

As Tgbox built on `Telethon <https://github.com/LonamiWebs/Telethon>`_, you can access full power of this beautiful library.

.. code-block:: python
        
    ... # some code was omitted
    
    my_account = await drb.ta.TelegramClient.get_me()
    print(my_account.first_name, my_account.id) 

- See a `Telethon documentation <https://docs.telethon.dev/>`_.
