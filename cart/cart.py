from dashboard.models import Document


class Cart():
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('session_key')
        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}
        self.cart = cart

    def add(self, document):
        document_id = str(document.id)
        if document_id in self.cart:
            pass
        else:
            self.cart[document_id] = {'cost': str(document.cost)}
        self.session.modified = True

    def __len__(self):
        return len(self.cart)

    def get_docs(self):
        # Get ids from cart
        doc_ids = self.cart.keys()
        documents = Document.objects.filter(id__in=doc_ids)
        return documents

    def delete(self, document):
        document_id = str(document.id)
        # Delete from dictionary/cart
        if document_id in self.cart:
            del self.cart[document_id]

        self.session.modified = True

    def cart_total(self):
        # Get document IDS
        document_ids = self.cart.keys()
        # lookup those keys in our documents database model
        documents = Document.objects.filter(id__in=document_ids)
        # Get quantities
        quantities = self.cart
        # Start counting at 0
        total = 0

        for key, value in quantities.items():
            key = int(key)
            for doc in documents:
                if doc.id == key:
                    total = total + (doc.cost)
        return total

    def clear(self):
        self.cart = {}
        self.session['session_key'] = {}
        self.session.modified = True
