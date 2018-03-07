from handlers import process_message

def test_gerrit_change():
    message, attachments = process_message("https://review.lineageos.org/#/c/208421/")
    assert not message
    assert attachments
    assert len(attachments) == 1

def test_gerrit_changes():
    message, attachments = process_message("https://review.lineageos.org/#/c/208421/ https://review.lineageos.org/#/c/206154/")
    assert not message
    assert attachments
    assert len(attachments) == 2

def test_gerrit_changes_max():
    message, attachments = process_message("https://review.lineageos.org/#/c/208421/ https://review.lineageos.org/#/c/206154/ https://review.lineageos.org/#/c/206672/ https://review.lineageos.org/#/c/206003/ https://review.lineageos.org/#/c/197715/")
    assert not message
    assert attachments
    assert len(attachments) == 4

def test_vend():
    message, attachments = process_message("!vend")
    assert message
    assert not attachments

def test_karma():
    message, attachments = process_message("Some karma event")
    assert message == "BOT HAS PIMPED VARIOUS KARMA"
    assert not attachments

def test_cve():
    message, attachments = process_message("CVE-2017-5753")
    print(attachments)
    assert not message
    assert attachments
    assert len(attachments) == 1

if __name__ == "__main__":
    test_cve()
