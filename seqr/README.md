**Testing**

To run server-side django tests:

```
cd $SEQR_ROOT
python -Wmodule -u manage.py test -p '*_tests.py' -v 2
```


To run client-side tests:

```
cd $SEQR_ROOT/ui
npm test
```
