from flask import Flask, request, jsonify
from pyotrs import Client, Article ,Ticket

app = Flask(__name__)

client = Client("http://app.autointelli.com:10480","root@localhost","fdPSRazwDP7wzJed")
client.session_create()

@app.route("/create_ticket", methods=["POST"])
def create_ticket():
    data = request.get_json()
    queue = data["queue"]
    title = data["title"]
    state = data["state"]
    priority = data["priority"]
    customer_user = data["customer_user"]
    subject = data["subject"]
    body = data["body"]

    ticket = Ticket.create_basic(Title=title,
                                 Queue=queue,
                                 State=state,
                                 Priority=priority,
                                 CustomerUser=customer_user
                                ) 
    
    data = Article({"Subject": subject,"Body": body})
    try:
        ticket_id = client.ticket_create(ticket, data)
        return jsonify({"message": f"Ticket created successfully! ID: {ticket_id}"})

    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/tickets/all" , methods=["GET"])
def get_all_tickets():
    tickets = client.ticket_search()
    return jsonify(tickets)

@app.route("/tickets/<int:ticket_id>", methods=["GET"])
def get_ticket(ticket_id):
    try:
        ticket = client.ticket_get_by_id(ticket_id)
        my_ticket = ticket.to_dct()
        return jsonify(my_ticket)

    except Exception as e:
        print(f"Error retrieving ticket: {e}")
        return jsonify({"error": "Ticket not found"})

@app.route('/tickets', methods=['GET'])
def get_tickets():
    try:
        ticket_ids = client.ticket_search()
        my_tickets = client.ticket_get_by_list(ticket_ids)
        ticket_list = []
        for ticket in my_tickets:
            ticket_data = ticket.to_dct()
            ticket_list.append(ticket_data)

        return jsonify(ticket_list)

    except Exception as e:
        print(f"Error retrieving ticket: {e}")
        return jsonify({"error": "Ticket not found"})


@app.route('/tickets/data', methods=['GET'])
def get_tickets_particular():
    try:
        ticket_ids = client.ticket_search()
        my_tickets = client.ticket_get_by_list(ticket_ids)
        ticket_list = []
        for ticket in my_tickets:
            ticket_number = ticket.field_get("TicketNumber")
            ticket_id = ticket.field_get("TicketID")
            ticket_title = ticket.field_get("Title")
            ticket_priority = ticket.field_get("Priority")
            ticket_queue = ticket.field_get("Queue")
            ticket_age = ticket.field_get("Age")
            ticket_created = ticket.field_get("Created")
            
            ticket_data = {
                'TicketNumber': ticket_number,
                'TicketID' : ticket_id,
                'Title': ticket_title,
                'Priority': ticket_priority,
                'Queue': ticket_queue,
                'Age': ticket_age,
                'Created': ticket_created
            }
            ticket_list.append(ticket_data)

        return jsonify(ticket_list)

    except Exception as e:
        print(f"Error retrieving ticket: {e}")
        return jsonify({"error": "Ticket not found"}) 

@app.route("/update_ticket/<int:ticket_id>", methods=["PUT"])
def update_ticket(ticket_id):
    try:
        data = request.json
        if "title" in data:
            client.ticket_update(ticket_id, Title=data["title"])

        if "queue" in data:
            client.ticket_update(ticket_id, Queue=data["queue"])

        if "state" in data:
            client.ticket_update(ticket_id, State=data["state"])

        if "body" in data and "subject" in data:
            my_article = Article({"Subject": data["subject"], "Body": data["body"]})
            client.ticket_update(ticket_id, article=my_article)

        return jsonify({"message": "Ticket updated successfully"})

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
