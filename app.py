from flask import Flask, render_template, request, redirect, flash, session
import pandas as pd
import mysql.connector
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

@app.after_request
def add_no_cache(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

app.secret_key = os.getenv("SECRET_KEY")

db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT")),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)


cursor = db.cursor()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        sql = "SELECT * FROM users WHERE username=%s AND password=%s"
        values = (username, password)

        cursor.execute(sql, values)

        user = cursor.fetchone()

        if user:
            session["username"] = user[3]
            session["role"] = user[5]
            session["owner_name"] = user[2]
            session["shop_name"] = user[1]
            return redirect("/dashboard")
          
        else:
            return "Invalid Username or Password"

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "owner_name" not in session:
        return redirect("/login")

    cursor = db.cursor()

    query = """
    SELECT COUNT(*)
    FROM products
    """

    cursor.execute(query)

    total_products = cursor.fetchone()[0]


    query = """
    SELECT SUM(current_stock)
    FROM products
    """

    cursor.execute(query)

    total_stock = cursor.fetchone()[0]

    query = """
    SELECT COUNT(*)
    FROM products
    WHERE current_stock > 0
    AND current_stock <= minimum_stock
    """

    cursor.execute(query)

    low_stock = cursor.fetchone()[0]
    query = """
    SELECT COALESCE(SUM(quantity), 0)
    FROM stock_history
    WHERE action = 'IN'
    AND date = CURDATE()
    """

    cursor.execute(query)

    today_stock_in = cursor.fetchone()[0]

    query = """
    SELECT COALESCE(SUM(quantity), 0)
    FROM stock_history
    WHERE action = 'OUT'
    AND date = CURDATE()
    """

    cursor.execute(query)

    today_stock_out = cursor.fetchone()[0]

    return render_template(
    "dashboard.html",
     role=session["role"],
    total_products=total_products,
    total_stock=total_stock,
    low_stock=low_stock,
    today_stock_in=today_stock_in,
    today_stock_out=today_stock_out,
    owner_name=session["owner_name"]
)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/low_stock")
def low_stock():

    cursor = db.cursor()

    query = """
            SELECT
                product_code,
                product_name,
                mrp,
                current_stock,
                minimum_stock,
                (minimum_stock - current_stock) AS short_by
            FROM products
            WHERE current_stock <= minimum_stock
            ORDER BY (minimum_stock - current_stock) DESC
            """

    cursor.execute(query)

    products = cursor.fetchall()

    return render_template(
        "low_stock.html",
        products=products
    )

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        shop_name = request.form["shop_name"]
        owner_name = request.form["owner_name"]
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            return "Passwords do not match!"

        sql = """
        INSERT INTO users(shop_name, owner_name, username, password)
        VALUES(%s, %s, %s, %s)
        """

        values = (shop_name, owner_name, username, password)

        cursor.execute(sql, values)
        db.commit()

        return "🎉 Account Created Successfully!"

    return render_template("signup.html")

@app.route("/add_product", methods=["GET", "POST"])
def add_product():
    if session["role"] != "Admin":
        return redirect("/dashboard")
    if request.method == "POST":

        product_code = request.form["product_code"]
        product_name = request.form["product_name"]
        mrp = request.form["mrp"]
        current_stock = request.form["current_stock"]
        minimum_stock = request.form["minimum_stock"]
        brand_id = request.form["brand_id"]

        sql = """
        INSERT INTO products
        (product_code, product_name, mrp, current_stock, minimum_stock, brand_id, user_id)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
        """

        values = (
            product_code,
            product_name,
            mrp,
            current_stock,
            minimum_stock,
            brand_id,
            1
        )

        cursor.execute(sql, values)
        db.commit()

        return "✅ Product Added Successfully!"

    return render_template("add_product.html")

@app.route("/view_products", methods=["GET", "POST"])
def view_products():

    page = request.args.get("page", 1, type=int)
    per_page = 25

    search = ""

    cursor = db.cursor()

    if request.method == "POST":

        search = request.form["search"]

        cursor.execute("""
            SELECT COUNT(*)
            FROM products
            WHERE product_code LIKE %s
               OR product_name LIKE %s
        """, ("%" + search + "%", "%" + search + "%"))

        total_products = cursor.fetchone()[0]

        offset = (page - 1) * per_page

        cursor.execute("""
            SELECT product_code,
                   product_name,
                   mrp,
                   current_stock,
                   minimum_stock
            FROM products
            WHERE product_code LIKE %s
               OR product_name LIKE %s
            LIMIT %s OFFSET %s
        """, (
            "%" + search + "%",
            "%" + search + "%",
            per_page,
            offset
        ))

    else:

        cursor.execute("SELECT COUNT(*) FROM products")
        total_products = cursor.fetchone()[0]

        offset = (page - 1) * per_page

        cursor.execute("""
            SELECT product_code,
                   product_name,
                   mrp,
                   current_stock,
                   minimum_stock
            FROM products
            LIMIT %s OFFSET %s
        """, (per_page, offset))

    products = cursor.fetchall()

    total_pages = (total_products + per_page - 1) // per_page

    return render_template(
        "view_products.html",
        products=products,
        page=page,
        total_pages=total_pages,
        search=search
    )


@app.route("/edit_product/<product_code>", methods=["GET", "POST"])
def edit_product(product_code):
    if session["role"] != "Admin":
        return redirect("/dashboard")
    cursor = db.cursor()
    if request.method == "POST":

        product_name = request.form["product_name"]
        mrp = request.form["mrp"]
        current_stock = request.form["current_stock"]
        minimum_stock = request.form["minimum_stock"]

        query = """
        UPDATE products
        SET
            product_name = %s,
            mrp = %s,
            current_stock = %s,
            minimum_stock = %s
        WHERE product_code = %s
        """

        cursor.execute(
            query,
            (
                product_name,
                mrp,
                current_stock,
                minimum_stock,
                product_code
            )
        )

        db.commit()

        return redirect("/view_products")
    if request.method == "GET":

        query = """
        SELECT product_code,
               product_name,
               mrp,
               current_stock,
               minimum_stock
        FROM products
        WHERE product_code = %s
        """

        cursor.execute(query, (product_code,))

        product = cursor.fetchone()

        return render_template(
            "edit_product.html",
            product=product
        )
       
@app.route("/delete_product/<product_code>")
def delete_product(product_code):
    if session["role"] != "Admin":
        return redirect("/dashboard")
    cursor = db.cursor()

    query = """
    DELETE FROM products
    WHERE product_code = %s
    """

    cursor.execute(query, (product_code,))
    db.commit()

    return redirect("/view_products")
    
@app.route("/products")
def products():
    return render_template("products.html")

def find_column(row, possible_names):

    for column in possible_names:

        if column in row.index:
            return row[column]

    return None


@app.route("/import_excel", methods=["GET", "POST"])
def import_excel():
    if session["role"] != "Admin":
        return redirect("/dashboard")
    if request.method == "POST":

       excel = request.files["excel_file"]

       print(excel.filename)

       # Get all sheet names
       # Detect file type
       filename = excel.filename.lower()
 
       if filename.endswith(".xlsb"):
           engine = "pyxlsb"

       elif filename.endswith(".xlsx"):
            engine = "openpyxl"

       else:
          return "❌ Only .xlsb and .xlsx files are supported."


     # Open workbook
       xls = pd.ExcelFile(excel, engine=engine)
       sheet_names = xls.sheet_names


        # If only one sheet exists
       if len(sheet_names) == 1:

          df = pd.read_excel(
          excel,
          engine=engine
          )

      # If multiple sheets exist
       else:

          if "MRP" in sheet_names:

              df = pd.read_excel(
               excel,
              sheet_name="MRP",
              engine=engine
             )

          else:

              return f"❌ MRP sheet not found.<br>Available Sheets: {sheet_names}"


       for index, row in df.iterrows():

         product_code = find_column(row, ["Material", "Product Code", "SKU", "Item Code"])

         product_name = find_column(row, ["Description", "Product Name", "Item Name", "Name"])

         mrp = find_column(row, ["MRP", "Price", "Selling Price"])

         segment = find_column(row, ["SEGMENT", "Segment"])
         current_stock = 0
         minimum_stock = 0
         brand_id = 1
         user_id = 1
         
         query = """
         INSERT INTO products
         (product_code, product_name, mrp, current_stock, minimum_stock, brand_id, user_id)
         VALUES (%s, %s, %s, %s, %s, %s, %s)
         """
         cursor.execute(
            query,
            (
                product_code,
                product_name,
                mrp,
                current_stock,
                minimum_stock,
                brand_id,
                user_id
            )
          )
         

       db.commit()
       return "Products Imported Successfully!"  

    return render_template("import_excel.html")


@app.route("/search_product", methods=["GET", "POST"])

def search_product():
    products = []
    searched = False

    if request.method == "POST":
        searched = True
        search = request.form["search"]

        cursor = db.cursor()

        query = """
        SELECT *
        FROM products
        WHERE product_code LIKE %s
        OR product_name LIKE %s
        """

        cursor.execute(query, ("%" + search + "%", "%" + search + "%"))

        products = cursor.fetchall()

        return render_template(
        "search_product.html",
        products=products,
        searched=searched
        )

    return render_template(
    "search_product.html",
    products=[],
    searched=False
    )

@app.route("/inventory")
def inventory():

    return render_template("inventory.html")

@app.route("/stock_in", methods=["GET", "POST"])
def stock_in():
    if session["role"] != "Admin":
        return redirect("/dashboard")
    product = None
    success = ""
    

    if request.method == "POST":
        action = request.form.get("action")
        if action != "add_stock":

            search = request.form["product_code"]

            cursor = db.cursor()

            query = """
            SELECT *
            FROM products
            WHERE product_code = %s
            """

            cursor.execute(query, (search,))

            product = cursor.fetchone()

        else:

            product_code = request.form["product_code"]

            quantity = int(request.form["quantity"])

            cursor = db.cursor()
            
            db.commit()
            query = """
            UPDATE products
            SET current_stock = current_stock + %s
            WHERE product_code = %s
            """

            cursor.execute(query, (quantity, product_code))

            db.commit()
            query = """
            SELECT *
            FROM products
            WHERE product_code = %s
            """

            cursor.execute(query, (product_code,))

            product = cursor.fetchone()
            
            query = """
            INSERT INTO stock_history
            (
            product_code,
            product_name,
            action,
            quantity,
            date,
            time,
            done_by,
            role
            )
            
            VALUES
            (
            %s,
            %s,
            %s,
            %s,
            CURDATE(),
            CURTIME(),
            %s,
            %s
            )
            """

            done_by = session["owner_name"]
            role = session["role"]

            try:
                cursor.execute(query, (
                    product[1],
                    product[2],
                    "IN",
                    quantity,
                    done_by,
                    role
                ))
                db.commit()
                print("History Inserted Successfully")

            except Exception as e:
                print(e)
            
            success = "✅ Stock Updated Successfully"

        search = request.form["product_code"]

        cursor = db.cursor()

        query = """
        SELECT *
        FROM products
        WHERE product_code = %s
        """

        cursor.execute(query, (search,))

        product = cursor.fetchone()

    return render_template(
        "stock_in.html",
        product=product,
        success=success
    )

@app.route("/stock_out", methods=["GET", "POST"])
def stock_out():
    product = None
    success = ""
    

    if request.method == "POST":
        action = request.form.get("action")
        if action != "minus_stock":

            search = request.form["product_code"]

            cursor = db.cursor()

            query = """
            SELECT *
            FROM products
            WHERE product_code = %s
            """

            cursor.execute(query, (search,))

            product = cursor.fetchone()

        else:
            
            product_code = request.form["product_code"]
      
            quantity = int(request.form["quantity"])
            cursor = db.cursor()

            query = """
            SELECT current_stock
            FROM products
            WHERE product_code = %s
            """

            cursor.execute(query, (product_code,))

            current_stock = cursor.fetchone()[0]
            if quantity > current_stock:

                success = "❌ Not enough stock available."

            else:
                cursor = db.cursor()

                query = """
                UPDATE products
                SET current_stock = current_stock - %s
                WHERE product_code = %s
                """

                cursor.execute(query, (quantity, product_code))

                db.commit()
                query = """
                SELECT *
                FROM products
                WHERE product_code = %s
                """

                cursor.execute(query, (product_code,))

                product = cursor.fetchone()
                query = """
                INSERT INTO stock_history
                (
                product_code,
                product_name,
                action,
                quantity,
                date,
                time,
                done_by,
                role
                )
                            
                VALUES
                (
                %s,
                %s,
                %s,
                %s,
                CURDATE(),
                CURTIME(),
                %s,
                %s
                )
                """

                done_by = session["owner_name"]
                role = session["role"]
                try:
                    cursor.execute(query, (
                    product[1],
                    product[2],
                    "OUT",
                    quantity ,
                    done_by,
                    role                                                                             
                    ))
                    db.commit()
                    print("History Inserted Successfully")
                                                                            
                except Exception as e:
                    print(e)
                success = "✅ Stock Updated Successfully"

            search = request.form["product_code"]

            cursor = db.cursor()

            query = """
            SELECT *
            FROM products
            WHERE product_code = %s
            """

            cursor.execute(query, (search,))

            product = cursor.fetchone()

    return render_template(
        "stock_out.html",
        product=product,
        success=success
    )


@app.route("/stock_history", methods=["GET", "POST"])
def stock_history():

    cursor = db.cursor()

    search = ""

    if request.method == "POST":

        search = request.form["search"]

        query = """
        SELECT *
        FROM stock_history
        WHERE product_code = %s
        OR product_name LIKE %s
        ORDER BY id DESC
        """

        cursor.execute(query, (search, "%" + search + "%"))

    else:

        query = """
        SELECT *
        FROM stock_history
        ORDER BY id DESC
        """

        cursor.execute(query)

    history = cursor.fetchall()

    history = [
    row[:6] + ((row[6] + timedelta(hours=5, minutes=30)) % timedelta(days=1),) + row[7:]
    for row in history
    ]

    return render_template(
        "stock_history.html",
        history=history,
        search=search
    )


@app.route("/settings")
def settings():
    return render_template("settings.html")

@app.route("/inventory_settings")
def inventory_settings():
    
    return render_template("inventory_settings.html")

@app.route("/search_inventory_settings", methods=["POST"])
def search_inventory_settings():

    search = request.form["search"]

    cursor = db.cursor()

    query = """
    SELECT
        product_code,
        product_name,
        current_stock,
        minimum_stock
    FROM products
    WHERE product_code = %s
       OR product_name LIKE %s
    """

    cursor.execute(query, (search, "%" + search + "%"))

    products = cursor.fetchall()

    return render_template(
        "inventory_settings.html",
        products=products,
        search=search
    )

@app.route("/update_min_stock", methods=["POST"])
def update_min_stock():
    if session["role"] != "Admin":
        return redirect("/dashboard")
    product_code = request.form["product_code"]

    minimum_stock = request.form["minimum_stock"]

    cursor = db.cursor()

    query = """
    UPDATE products
    SET minimum_stock = %s
    WHERE product_code = %s
    """

    cursor.execute(query, (minimum_stock, product_code))

    db.commit()
    flash("Minimum Stock Updated Successfully!", "success")
    return redirect("/inventory_settings")


@app.route("/change_password", methods=["GET", "POST"])
def change_password():

    if request.method == "GET":
        return render_template("change_password.html")

    current_password = request.form["current_password"]
    new_password = request.form["new_password"]
    confirm_password = request.form["confirm_password"]

    cursor = db.cursor()

    username = session["username"]

    query = """
    SELECT password
    FROM users
    WHERE username = %s
    """

    cursor.execute(query, (username,))

    result = cursor.fetchone() 
    if result[0] != current_password:

        return render_template(
            "change_password.html",
            error="Current password is incorrect."
        )
    if new_password != confirm_password:

        return render_template(
            "change_password.html",
            error="Passwords do not match."
        )
    query = """
    UPDATE users
    SET password = %s
    WHERE username = %s
    """

    cursor.execute(query, (new_password, username))

    db.commit()
    return render_template(
    "change_password.html",
    success="Password changed successfully."
    )


@app.route("/employee_management")
def employee_management():
    if session["role"] != "Admin":
        return redirect("/dashboard")
    

    cursor = db.cursor()

    cursor.execute("""
        SELECT owner_name, username, role
        FROM users
    """)

    employees = cursor.fetchall()

    return render_template(
        "employee_management.html",
        employees=employees
    )

@app.route("/add_employee", methods=["POST"])
def add_employee():

    if session["role"] != "Admin":
        return redirect("/dashboard")

    name = request.form["owner_name"]
    username = request.form["username"]
    password = request.form["password"]

    cursor = db.cursor()

    query = """
    INSERT INTO users (owner_name, username, password, role)
    VALUES (%s, %s, %s, 'Employee')
    """

    cursor.execute(query, (name, username, password))
    db.commit()

    return redirect("/employee_management")

@app.route("/delete_employee/<username>")
def delete_employee(username):

    if session["role"] != "Admin":
        return redirect("/dashboard")

    cursor = db.cursor()

    query = """
    DELETE FROM users
    WHERE username = %s
    """

    cursor.execute(query, (username,))
    db.commit()

    return redirect("/employee_management")


if __name__ == "__main__":
    app.run(debug=True)