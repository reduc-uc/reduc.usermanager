from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm


suspend_vocabulary = SimpleVocabulary.fromItems((
        (u'Cuenta vencida', '*s*'),
        (u'Password Obvio', '*o*'),
        (u'Cuenta hackeada', '*h*'),
        ))

