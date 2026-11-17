"""OOP guides for the CS fundamentals track (Prep). Checked by check_prep.py."""

GUIDES = [
    dict(
        id='guide-cs-fundamentals-oop-classes-and-objects', kind='guide', track='cs-fundamentals', subject='OOP',
        title='Classes and objects', order=1,
        summary="A class is a blueprint that describes state and behaviour, and an object is one concrete instance built from it at runtime.",
        sections=[
            dict(title='Blueprint versus instance', text=(
                "A class is a definition. It says what data each instance will hold (its fields) and what it can do (its methods). "
                "An object is a real thing in memory, created from that definition, with its own copy of the fields.\n\n"
                "Think of a class Account with fields owner and balance and a method deposit. Writing the class creates no accounts. "
                "Each time you write new Account(), the JVM allocates a fresh object on the heap, and two accounts can hold different balances at the same time.\n\n"
                "A useful way to say it in an interview: the class defines the type, and objects are values of that type. "
                "One class can produce any number of objects, and every object knows which class it came from. "
                "State is what an object knows, behaviour is what it can do, and identity is what makes it a separate object even when its state matches another one."
            )),
            dict(title='Constructors and the new keyword', text=(
                "A constructor is a special block that runs once when an object is created. It has the same name as the class and no return type, not even void. "
                "Its job is to put the object into a valid starting state.\n\n"
                "class Point { int x, y; Point(int x, int y) { this.x = x; this.y = y; } }\n\n"
                "Here this.x refers to the field and plain x refers to the parameter. "
                "If you write no constructor at all, Java supplies a default no-argument constructor for you. "
                "The moment you write any constructor yourself, that free default disappears, so new Point() would no longer compile unless you add a no-argument version too. "
                "This catches many students out.\n\n"
                "Constructors can be overloaded, and one constructor can call another with this(...) as its first statement. "
                "Fields you do not set get default values: 0 for numbers, false for booleans and null for references. Local variables get no default and must be assigned before use."
            )),
            dict(title='Instance members and static members', text=(
                "An instance field belongs to each object separately. A static field belongs to the class itself, so there is exactly one copy shared by every object.\n\n"
                "class Counter { static int created = 0; int id; Counter() { created++; id = created; } }\n\n"
                "After three new Counter() calls, Counter.created is 3, while the three objects have ids 1, 2 and 3.\n\n"
                "Static methods follow the same rule. They run without any object, so there is no this inside them. "
                "That is why a static method cannot read an instance field directly: it would not know which object's field you mean. "
                "It can still work with instance data if you hand it an object reference. "
                "The classic public static void main is static for exactly this reason, because the JVM must call it before any object of your class exists."
            )),
            dict(title='Variables hold references, not objects', text=(
                "In Java, a variable of a class type does not contain the object. It holds a reference that points to the object.\n\n"
                "Point a = new Point(1, 2); Point b = a; Point c = new Point(1, 2);\n\n"
                "This creates two objects, not three. a and b point to the same object, so changing b.x also changes what you see through a. "
                "c points to a separate object that merely has the same values.\n\n"
                "The == operator on references asks whether two variables point to the same object. So a == b is true and a == c is false. "
                "To compare contents you call equals, but only if the class overrides it. "
                "The version inherited from Object behaves just like ==, so without an override a.equals(c) is also false. "
                "A common misconception is that equals compares fields automatically. It does not; you, or a record, must define that."
            )),
        ],
        keyPoints=[
            'A class is a definition; an object is a runtime instance with its own copy of the instance fields.',
            'Writing any constructor removes the default no-argument constructor Java would otherwise supply.',
            'Static members belong to the class and are shared; static methods have no this.',
            'Class-type variables hold references, so assignment copies the reference, not the object.',
            '== checks identity; equals checks content only when the class overrides it.',
        ],
        challenges=[
            dict(id='challenge-oop-classes-and-objects-q1', kind='prediction', title='Counting objects',
                 prompt="Point a = new Point(1, 2); Point b = a; Point c = new Point(1, 2); How many Point objects exist after these lines?",
                 options=['1', '2', '3'], answer=1,
                 explanation="Only the two new expressions create objects. Point b = a copies the reference, so a and b point to the same object. Three would be right only if assignment copied objects, which Java never does for class types.",
                 hint='Count the uses of new, not the variables.'),
            dict(id='challenge-oop-classes-and-objects-q2', kind='prediction', title='Shared counter',
                 prompt="class Counter { static int count = 0; Counter() { count++; } } If you create three Counter objects, what is Counter.count?",
                 options=['1, because each object has its own count', '0, because static fields cannot be changed in a constructor', '3', 'It does not compile'],
                 answer=2,
                 explanation="count is static, so there is one copy shared by all objects. Each constructor call increments that single copy, giving 3. It would be 1 per object only if count were an instance field, and constructors are free to modify static fields.",
                 hint='Ask how many copies of a static field exist.'),
            dict(id='challenge-oop-classes-and-objects-q3', kind='prediction', title='The missing constructor',
                 prompt="class Box { int size; Box(int size) { this.size = size; } } Elsewhere you write: Box b = new Box(); What happens?",
                 options=['Compile error: there is no Box() constructor', 'It compiles and size defaults to 0', 'It compiles but throws an exception at runtime'],
                 answer=0,
                 explanation="Java only supplies a default no-argument constructor when the class declares no constructors at all. Box declares Box(int), so Box() does not exist and the call fails at compile time. size would indeed default to 0 in a newly created Box, but here no Box is ever created because the code does not compile.",
                 hint='When does Java add the default constructor for you?'),
            dict(id='challenge-oop-classes-and-objects-q4', kind='prediction', title='Identity versus equality',
                 prompt="Point does not override equals. Point a = new Point(1, 2); Point c = new Point(1, 2); What are a == c and a.equals(c)?",
                 options=['true and true', 'false and true', 'false and false', 'true and false'],
                 answer=2,
                 explanation="a and c are different objects, so == is false. Without an override, equals is inherited from Object, which also checks identity, so it is false as well. false and true would need an equals override that compares x and y.",
                 hint='What does the equals method inherited from Object actually compare?'),
            dict(id='challenge-oop-classes-and-objects-q5', kind='prediction', title='Static meets instance',
                 prompt="class User { String name; static void greet() { System.out.println(name); } } What happens when you compile this?",
                 options=['It prints the name of the most recently created User', 'Compile error: a static method cannot use an instance field without an object', 'It prints null'],
                 answer=1,
                 explanation="A static method runs without any object, so there is no this and no way to know whose name to read. The compiler rejects it. Java never picks a recent object for you, and it never gets far enough to print null.",
                 hint='Inside a static method, which object would name belong to?'),
        ],
    ),
    dict(
        id='guide-cs-fundamentals-oop-encapsulation', kind='guide', track='cs-fundamentals', subject='OOP',
        title='Encapsulation', order=2,
        summary="Encapsulation keeps an object's data private and exposes only the operations that keep that data valid.",
        sections=[
            dict(title='What encapsulation really means', text=(
                "Encapsulation means bundling data with the methods that work on it, and controlling access so outside code cannot put the object into a broken state.\n\n"
                "The key idea is the invariant: a rule that must always hold for the object. For a bank account it might be that the balance never goes below zero. "
                "If balance is a public field, any line anywhere in the program can write account.balance = -500, and nothing stops it. "
                "If balance is private and the only ways to change it are deposit and withdraw, those two methods can check the rule every time.\n\n"
                "So encapsulation is not mainly about hiding things for secrecy. It is about having one place that owns the rules for a piece of data. "
                "A side benefit is freedom to change: callers depend on the methods, not the fields, so you can change the internal representation later without breaking them."
            )),
            dict(title='Access modifiers in Java', text=(
                "Java gives you four access levels, from tightest to loosest.\n\n"
                "private: visible only inside the declaring class. "
                "No modifier (package-private, often called default): visible to any class in the same package. "
                "protected: everything package-private allows, plus subclasses in other packages through inheritance. "
                "public: visible everywhere.\n\n"
                "Two details are often missed. First, protected is wider than default, not narrower, because it includes the whole package. "
                "Second, private is checked per class, not per object. A method in Account can read other.balance of a different Account object, because the code is inside the Account class. "
                "That is why equals methods can compare private fields directly.\n\n"
                "A sensible default is to make fields private and widen access only when you have a reason."
            )),
            dict(title='Getters and setters are not automatically encapsulation', text=(
                "A private field with a plain getter and a plain setter is barely better than a public field. If setBalance accepts any number, the invariant is still unprotected.\n\n"
                "Better designs expose meaningful operations instead of raw writes. deposit(amount) can reject negative amounts, and withdraw(amount) can refuse to overdraw. "
                "Ask what the caller wants to do, not which field they want to touch.\n\n"
                "Getters can leak too. If an Order keeps a private List of items and getItems() returns that same list, the caller can call clear() on it and empty your order behind your back. "
                "The field is private but the object it points to is not protected. "
                "The fix is to return a copy or an unmodifiable view, for example List.copyOf(items) or Collections.unmodifiableList(items). "
                "The same applies in constructors: copy mutable arguments you store, so the caller cannot change them later."
            )),
            dict(title='Encapsulation versus abstraction', text=(
                "Interviewers often ask for the difference, and the two are easy to blur.\n\n"
                "Abstraction is about design: deciding what a type should expose and what details callers should not need to think about. "
                "Encapsulation is about enforcement: using access control to keep the internals behind that boundary. "
                "One way to remember it: abstraction chooses the interface, encapsulation protects the implementation.\n\n"
                "A strong form of encapsulation is immutability. If a class has only private final fields, sets them in the constructor, offers no methods that change them and never hands out its mutable internals, "
                "then once an object is built it can never become invalid. String is the classic example. "
                "Immutable objects are also safe to share between threads without locking, which is a good point to mention when asked why encapsulation matters."
            )),
        ],
        keyPoints=[
            'Encapsulation protects invariants by routing every change through methods that check the rules.',
            'Access levels from narrow to wide: private, package-private, protected, public.',
            'private is per class, not per object: an instance can read another instance\'s private fields.',
            'A setter that accepts anything, or a getter that returns a mutable internal object, breaks encapsulation.',
            'Abstraction decides what to expose; encapsulation enforces that the rest stays hidden.',
        ],
        challenges=[
            dict(id='challenge-oop-encapsulation-q1', kind='prediction', title='No modifier',
                 prompt="A field in class A has no access modifier. Which class can read it directly?",
                 options=['Any class in any package', 'Only subclasses of A, wherever they are', 'Any class in the same package as A, subclass or not', 'Only A itself'],
                 answer=2,
                 explanation="No modifier means package-private: every class in the same package can access it, and nothing outside the package can, even a subclass. Subclasses in other packages need protected. Only A itself would be private.",
                 hint='What is the default access level called?'),
            dict(id='challenge-oop-encapsulation-q2', kind='prediction', title='Leaky getter',
                 prompt="class Order { private List<String> items = new ArrayList<>(); public List<String> getItems() { return items; } } A caller runs order.getItems().clear(). What happens?",
                 options=['Nothing; the caller received a copy', 'The order\'s own item list is emptied', 'Compile error, because items is private'],
                 answer=1,
                 explanation="The getter returns the reference to the same list object the Order holds, so clear() empties the order's own data. Java does not copy objects on return. The code compiles because the caller never names the private field; it only calls a public method.",
                 hint='Does returning a reference copy the list?'),
            dict(id='challenge-oop-encapsulation-q3', kind='prediction', title='Guarding the balance',
                 prompt="You want an Account whose balance can never become negative. Which design actually guarantees that?",
                 options=['A private balance changed only through deposit and withdraw methods that validate the amount', 'A private balance with a public setBalance(double) and a getter', 'A public balance field with a comment saying it must stay positive'],
                 answer=0,
                 explanation="Only the first design gives the class a single checked path for every change. A setter that accepts any value lets callers write a negative number, and a comment enforces nothing.",
                 hint='Which option puts a check in front of every possible change?'),
            dict(id='challenge-oop-encapsulation-q4', kind='prediction', title='Private across objects',
                 prompt="class Account { private String owner; boolean sameOwner(Account other) { return owner.equals(other.owner); } } Does this compile?",
                 options=['No, other.owner is private to that other object', 'Yes, because private access is checked per class, not per object', 'Only if owner is declared final'],
                 answer=1,
                 explanation="Java access control works at the class level. Code inside Account may access the private fields of any Account instance, not just this. final has nothing to do with visibility.",
                 hint='Is private about which object or which class the code is in?'),
            dict(id='challenge-oop-encapsulation-q5', kind='prediction', title='Protected from outside',
                 prompt="Class A in package p has a protected field. Class B is in package q and does not extend A. Can B read the field?",
                 options=['Yes, protected behaves like public', 'Yes, as long as B imports A', 'Yes, but only from static methods', 'No, protected reaches the same package and subclasses only'],
                 answer=3,
                 explanation="protected allows access from the same package and from subclasses through inheritance. B is in another package and is not a subclass, so it has no access. Importing only makes the name usable; it never grants access, and static has no bearing on this.",
                 hint='List the two groups protected opens the field to.'),
        ],
    ),
    dict(
        id='guide-cs-fundamentals-oop-inheritance', kind='guide', track='cs-fundamentals', subject='OOP',
        title='Inheritance', order=3,
        summary="Inheritance lets a class extend another to reuse and specialise its behaviour, and it should model a true is-a relationship.",
        sections=[
            dict(title='Is-a relationships and extends', text=(
                "Inheritance lets a new class, the subclass or child, build on an existing class, the superclass or parent. "
                "The child gets the parent's accessible fields and methods and can add new ones or override existing behaviour.\n\n"
                "class Animal { void eat() { ... } } class Dog extends Animal { void bark() { ... } }\n\n"
                "A Dog can eat and bark. Every Dog is an Animal, so you can store one in an Animal variable.\n\n"
                "The test for using inheritance is the is-a question. A Dog is an Animal, so it fits. A Car is not an Engine, so Car extends Engine would be wrong even though a car uses one.\n\n"
                "In Java a class can extend only one class. It can, however, implement many interfaces. "
                "The usual reason given is the diamond problem: if a class inherited state and method bodies from two parents that both define the same method, which one should win would be ambiguous. "
                "Every class without an explicit parent extends Object."
            )),
            dict(title='Constructors and super', text=(
                "Constructors are not inherited, but they are chained. A parent constructor must finish before the child constructor can use the object it is building. "
                "If you do not write super(...) yourself, the compiler inserts a call to super() with no arguments as the first statement.\n\n"
                "class A { A() { System.out.print('A'); } } class B extends A { B() { System.out.print('B'); } }\n\n"
                "new B() prints AB: the parent part of the object is set up first, then the child part.\n\n"
                "This leads to a classic compile error. If the parent has only A(int x) and no no-argument constructor, the implicit super() has nothing to call. "
                "The child must then call super(someValue) explicitly. "
                "Classically, super(...) has to be the first statement in the constructor, and a constructor can call either this(...) or super(...), not both. "
                "Java 25 relaxed the ordering slightly: statements that do not touch the object under construction, such as argument checks, may now come before that call, but the one-call rule still holds.\n\n"
                "Outside constructors, super.method() calls the parent's version of a method you have overridden."
            )),
            dict(title='What is and is not inherited', text=(
                "A child object physically contains the parent's fields, including private ones, but the child's code cannot name the private ones directly. "
                "It has to go through public or protected methods of the parent. That is why people say private members are not inherited: they are not accessible, even though they exist.\n\n"
                "Private methods cannot be overridden. If a child declares a method with the same name as a private parent method, it is a new, unrelated method. "
                "Calls made inside the parent still reach the parent's private version.\n\n"
                "Static methods are not overridden either. A child static method with the same signature hides the parent one, and which version runs depends on the reference type, not the object.\n\n"
                "A final method cannot be overridden at all, and a final class cannot be extended. String is final for exactly this reason: nobody can subclass it and change its behaviour."
            )),
            dict(title='Composition over inheritance', text=(
                "Inheritance creates a tight link. A change in the parent can silently break children that relied on its internal behaviour, often called the fragile base class problem. "
                "The child also inherits every public method of the parent, whether it makes sense or not.\n\n"
                "Composition is the alternative: the class holds a reference to another object and delegates to it. "
                "class Car { private final Engine engine; void start() { engine.ignite(); } }\n\n"
                "This is a has-a relationship. You can swap in a different Engine, expose only the methods you choose, and test parts separately.\n\n"
                "A good rule for interviews: use inheritance when the child truly is a specialised kind of the parent and can be used anywhere the parent is expected. "
                "Use composition when you mainly want to reuse some code or when the relationship is has-a. Favouring composition is standard advice, not a ban on inheritance."
            )),
        ],
        keyPoints=[
            'Use inheritance only for a genuine is-a relationship; use composition for has-a.',
            'Java classes have single inheritance of classes but may implement many interfaces.',
            'Parent constructors always run first; the compiler inserts super() if you do not call one.',
            'Private methods, static methods and final methods are not overridden.',
            'Favour composition to avoid tight coupling and the fragile base class problem.',
        ],
        challenges=[
            dict(id='challenge-oop-inheritance-q1', kind='prediction', title='Constructor order',
                 prompt="class A { A() { System.out.print('A'); } } class B extends A { B() { System.out.print('B'); } } What does new B() print?",
                 options=['BA', 'AB', 'B', 'A'],
                 answer=1,
                 explanation="The compiler inserts super() as the first statement of B's constructor, so A's constructor finishes before B's body runs. BA gets the order backwards, and B alone ignores that the parent constructor always runs.",
                 hint='What is the hidden first line of every constructor that does not call this or super?'),
            dict(id='challenge-oop-inheritance-q2', kind='prediction', title='No default parent constructor',
                 prompt="class Parent { Parent(int x) { } } class Child extends Parent { Child() { } } What happens?",
                 options=['It compiles and x is passed as 0', 'It compiles but throws when a Child is created', 'Compile error: the implicit super() has no Parent() to call'],
                 answer=2,
                 explanation="Child() implicitly calls super(), but Parent only has Parent(int), so the compiler rejects it. Java never invents an argument, and the problem is found at compile time, not runtime. The fix is to call super(someValue) explicitly.",
                 hint='Which parent constructor does an empty child constructor try to call?'),
            dict(id='challenge-oop-inheritance-q3', kind='prediction', title='Why one parent',
                 prompt="Why does Java reject class C extends A, B?",
                 options=['Two parents could supply conflicting state and method bodies, making it ambiguous which to use', 'The JVM can only store one parent pointer per object', 'Multiple inheritance would make objects too large in memory'],
                 answer=0,
                 explanation="The design reason is ambiguity, often called the diamond problem: if A and B both define the same method or field, which one does C get? Memory size and pointer storage are not the reason; Java allows many interfaces, which shows the issue is about inherited implementation.",
                 hint='Think of two parents that both define the same method.'),
            dict(id='challenge-oop-inheritance-q4', kind='prediction', title='Car and Engine',
                 prompt="You are modelling a Car that uses an Engine. Which relationship is the best design?",
                 options=['Car extends Engine, since a car uses an engine', 'Engine extends Car, since an engine is part of a car', 'Both extend a shared Vehicle class', 'Car holds an Engine field and delegates to it'],
                 answer=3,
                 explanation="A car has an engine; it is not a kind of engine, and an engine is not a kind of car. That is a has-a relationship, which is composition. A shared Vehicle parent makes no sense for an engine.",
                 hint='Apply the is-a test in both directions.'),
            dict(id='challenge-oop-inheritance-q5', kind='prediction', title='Private method in the parent',
                 prompt="class Parent { private void log() { System.out.print('P'); } void run() { log(); } } class Child extends Parent { public void log() { System.out.print('C'); } } What does new Child().run() print?",
                 options=['C, because of dynamic dispatch', 'P, because private methods are not overridden', 'Compile error, because Child changes the access level'],
                 answer=1,
                 explanation="A private method is invisible to subclasses, so Child.log is a brand new method, not an override. run() in Parent calls Parent's private log, printing P. Dynamic dispatch only applies to overridable methods, and there is no access-level conflict because nothing is being overridden.",
                 hint='Can a subclass override something it cannot see?'),
        ],
    ),
    dict(
        id='guide-cs-fundamentals-oop-polymorphism', kind='guide', track='cs-fundamentals', subject='OOP',
        title='Polymorphism', order=4,
        summary="Polymorphism lets one call behave differently depending on types, through overloading at compile time and overriding at runtime.",
        sections=[
            dict(title='One call, many forms', text=(
                "Polymorphism means the same piece of code can work with values of different types and do the right thing for each. "
                "If you have a List<Shape> holding circles and squares, a loop calling shape.area() gets the circle formula for circles and the square formula for squares, without any if statements.\n\n"
                "Java has two kinds, and interviewers expect you to name both. "
                "Compile-time polymorphism, also called static binding, is method overloading: the compiler picks which method to call. "
                "Runtime polymorphism, also called dynamic dispatch, is method overriding: the JVM picks the method based on the actual object while the program runs.\n\n"
                "Runtime polymorphism is the one that makes OOP flexible. You can add a new Shape subclass later and the existing loop handles it without being edited."
            )),
            dict(title='Overloading is resolved at compile time', text=(
                "Overloading means several methods in the same class share a name but differ in their parameter list: the number of parameters, their types, or their order.\n\n"
                "int add(int a, int b) and double add(double a, double b) are valid overloads. "
                "int add(int a, int b) and long add(int a, int b) are not: the return type alone cannot tell them apart, so it is a compile error.\n\n"
                "The compiler chooses the overload using the declared types of the arguments, not the runtime object. "
                "Given show(Object o) and show(String s), the code Object x = \"hi\"; show(x); calls show(Object), because x is declared as Object. "
                "This surprises people who expect the more specific version.\n\n"
                "Overloading does not need inheritance at all. That is a key difference from overriding, which only exists between a parent and a child type."
            )),
            dict(title='Overriding and dynamic dispatch', text=(
                "Overriding happens when a subclass provides its own version of a method with the same name and parameter list as an inherited one.\n\n"
                "class Animal { String sound() { return \"...\"; } } class Dog extends Animal { @Override String sound() { return \"Woof\"; } }\n\n"
                "Animal a = new Dog(); a.sound() returns Woof. The variable's type is Animal, but the object is a Dog, and the JVM looks up the method on the object.\n\n"
                "Rules worth knowing: the overriding method cannot reduce visibility, so a public method cannot become private. "
                "The return type must be the same or a subtype, called a covariant return. "
                "It cannot throw broader checked exceptions. "
                "Static, private and final methods do not take part.\n\n"
                "Fields are never polymorphic. If both classes declare a field called name, a.name uses the reference type. "
                "Always add @Override so the compiler catches a typo that would otherwise create an accidental overload."
            )),
            dict(title='Reference type versus object type', text=(
                "A single rule explains most polymorphism puzzles. The reference type decides what you are allowed to call. The object type decides which version runs.\n\n"
                "With Animal a = new Dog(), a.sound() compiles because Animal declares sound, and it runs Dog's version. "
                "But a.bark() does not compile, even though the object really is a Dog, because the compiler only knows a as an Animal.\n\n"
                "Assigning a Dog to an Animal variable is upcasting and is always safe and implicit. "
                "Going back down needs an explicit cast: Dog d = (Dog) a. The compiler accepts any cast that could possibly succeed, so the check happens at runtime. "
                "If a actually points to a Cat, the cast throws ClassCastException. "
                "Use instanceof first when you are not sure, or better, redesign so the parent type has the method you need."
            )),
        ],
        keyPoints=[
            'Overloading: same name, different parameters, chosen at compile time from declared types.',
            'Overriding: same signature in a subclass, chosen at runtime from the actual object.',
            'Return type alone cannot distinguish overloads.',
            'Static, private and final methods are not overridden, and fields are never polymorphic.',
            'Reference type controls what you can call; object type controls which version runs.',
        ],
        challenges=[
            dict(id='challenge-oop-polymorphism-q1', kind='prediction', title='Which sound',
                 prompt="Dog extends Animal and overrides sound() to return Woof. Animal a = new Dog(); What does a.sound() return?",
                 options=["Animal's version, because a is declared as Animal", 'Woof', 'It does not compile'],
                 answer=1,
                 explanation="sound is an overridden instance method, so the JVM dispatches on the actual object, which is a Dog. The declared type only matters for deciding whether the call compiles, and it does because Animal declares sound.",
                 hint='For overridden methods, does the variable type or the object type decide?'),
            dict(id='challenge-oop-polymorphism-q2', kind='prediction', title='Overload choice',
                 prompt="A class has show(Object o) printing Object and show(String s) printing String. Object x = \"hi\"; show(x); What is printed?",
                 options=['String, since the object really is a String', 'Nothing; the call is ambiguous and does not compile', 'Object, since overloads are chosen from the declared type'],
                 answer=2,
                 explanation="Overload resolution happens at compile time using declared types. x is declared as Object, so only show(Object) matches. The runtime type is not consulted, and there is no ambiguity because show(String) simply does not apply to an Object argument.",
                 hint='When is an overload picked, and what does the compiler know about x?'),
            dict(id='challenge-oop-polymorphism-q3', kind='prediction', title='Return type only',
                 prompt="One class declares int add(int a, int b) and long add(int a, int b). What is this?",
                 options=['A compile error: return type alone does not distinguish overloads', 'Valid overloading', 'Valid overriding'],
                 answer=0,
                 explanation="Overloads must differ in their parameter lists. These two have identical parameters, so the compiler sees a duplicate method. It is not overriding either, since both are in the same class.",
                 hint='What part of a method signature does overloading look at?'),
            dict(id='challenge-oop-polymorphism-q4', kind='prediction', title='Fields and polymorphism',
                 prompt="class A { String name = \"A\"; } class B extends A { String name = \"B\"; } A obj = new B(); What does obj.name give?",
                 options=['B, because the object is a B', 'null', 'Compile error: name is declared twice', 'A, because fields are resolved by the reference type'],
                 answer=3,
                 explanation="Fields are not overridden; B's field hides A's. Field access is resolved from the declared type, which is A. Declaring a same-named field in a subclass is legal, and both fields are initialised, so neither null nor a compile error is right.",
                 hint='Is field access dynamic like method calls?'),
            dict(id='challenge-oop-polymorphism-q5', kind='prediction', title='Bad downcast',
                 prompt="Cat and Dog both extend Animal. Animal a = new Cat(); Dog d = (Dog) a; What happens?",
                 options=['Compile error: a Cat can never be a Dog', 'It compiles, then throws ClassCastException at runtime', 'It works and d sees the cat through the Dog type'],
                 answer=1,
                 explanation="The compiler only knows a is an Animal, which could be a Dog, so it allows the cast. At runtime the JVM sees the object is a Cat and throws ClassCastException. A cast never converts an object into a different class.",
                 hint='What does the compiler know about a, and what does the JVM know?'),
        ],
    ),
    dict(
        id='guide-cs-fundamentals-oop-abstraction-and-interfaces', kind='guide', track='cs-fundamentals', subject='OOP',
        title='Abstraction and interfaces', order=5,
        summary="Abstraction exposes what a type does and hides how, using abstract classes and interfaces as the tools.",
        sections=[
            dict(title='What abstraction means', text=(
                "Abstraction is showing the essential operations of something and hiding the details of how they are done. "
                "When you call list.add(x) you do not think about array resizing or node pointers. You rely on what add promises.\n\n"
                "In code, abstraction lets you write against a general type instead of a specific one. "
                "A method that takes a PaymentMethod and calls pay(amount) works for cards, wallets and bank transfers, including ones written next year.\n\n"
                "Java gives you two tools for this: abstract classes and interfaces. Both let you declare methods without bodies and force concrete classes to fill them in. "
                "Neither can be instantiated directly.\n\n"
                "Remember that abstraction is a design idea, while abstract classes and interfaces are language features that support it. "
                "A plain class with a clean public API is also an abstraction."
            )),
            dict(title='Abstract classes', text=(
                "A class marked abstract cannot be created with new, but it can be used as a type. "
                "Shape s = new Circle(2) is fine, and so is new Shape[3], because that creates an array, not a Shape.\n\n"
                "abstract class Shape { String label; Shape(String label) { this.label = label; } abstract double area(); String describe() { return label + \" \" + area(); } }\n\n"
                "An abstract class can have fields, constructors and fully written methods alongside abstract ones. "
                "The constructor runs when a subclass object is created, through super(...).\n\n"
                "If a class has even one abstract method, the class must be declared abstract. "
                "The reverse is not required: an abstract class may have no abstract methods at all, which is a way to stop direct instantiation. "
                "A concrete subclass must implement every inherited abstract method, or be declared abstract itself.\n\n"
                "Abstract classes suit a family of closely related types that share state and some code."
            )),
            dict(title='Interfaces', text=(
                "An interface is a contract: a set of methods a class promises to provide. A class can implement any number of interfaces.\n\n"
                "interface Payable { double RATE = 0.18; double amount(); }\n\n"
                "Interface methods without a body are implicitly public and abstract. Interface fields are implicitly public, static and final, so they are constants; trying to assign RATE in a class is a compile error. "
                "Interfaces have no constructors and no instance fields.\n\n"
                "Since Java 8 an interface can also hold default methods with a body, which implementing classes inherit, and static methods. "
                "Java 9 added private methods for sharing code between defaults.\n\n"
                "Because interface methods are public, the implementing method must be public too. Writing it with no modifier is a compile error, since that would reduce visibility.\n\n"
                "If a class implements two interfaces that both supply a default method with the same signature, it must override that method and can pick one with A.super.method()."
            )),
            dict(title='Choosing between them', text=(
                "This comparison is one of the most asked OOP questions.\n\n"
                "An abstract class can hold instance fields, constructors, and concrete methods at any access level; its abstract methods just cannot be private. A class can extend only one. "
                "An interface holds no instance state, its abstract methods are public, and a class can implement many.\n\n"
                "Choose an abstract class when related types share real state or setup logic, for example a base Employee with a name and id that every subclass needs. "
                "Choose an interface when you are describing a capability that unrelated classes might share, such as Comparable or Runnable, or when you want a class to fit several roles at once.\n\n"
                "An older misconception is that interfaces can never contain code. Default and static methods changed that in Java 8, but interfaces still cannot hold per-object state, which remains the clearest dividing line. "
                "A common pattern uses both: an interface for the contract and an abstract class that implements part of it."
            )),
        ],
        keyPoints=[
            'Abstraction exposes what a type does and hides how it does it.',
            'Abstract classes can have state, constructors and concrete methods but cannot be instantiated.',
            'Interface fields are public static final; abstract interface methods are public, so implementations must be public.',
            'Since Java 8 interfaces may have default and static methods, but never instance state.',
            'A class extends at most one class but may implement many interfaces.',
        ],
        challenges=[
            dict(id='challenge-oop-abstraction-and-interfaces-q1', kind='prediction', title='Which line fails',
                 prompt="Shape is an abstract class and Circle is a concrete subclass. Which line does not compile?",
                 options=['Shape s = new Circle();', 'Shape s = new Shape();', 'Shape[] shapes = new Shape[3];'],
                 answer=1,
                 explanation="You cannot instantiate an abstract class with new. Using Shape as a variable type is fine, and new Shape[3] creates an array of three null references, not any Shape objects, so it compiles too.",
                 hint='Which line actually tries to build a Shape object?'),
            dict(id='challenge-oop-abstraction-and-interfaces-q2', kind='prediction', title='Interface constant',
                 prompt="interface Config { int MAX = 10; } class App implements Config { void setUp() { MAX = 20; } } What happens?",
                 options=['MAX becomes 20 for App only', 'MAX becomes 20 for every class', 'Compile error: interface fields are implicitly public static final'],
                 answer=2,
                 explanation="Every field in an interface is implicitly final, so it cannot be reassigned anywhere. It is also static, so there is no per-class copy that App could change on its own.",
                 hint='Which modifiers does Java add to interface fields automatically?'),
            dict(id='challenge-oop-abstraction-and-interfaces-q3', kind='prediction', title='Abstract class facts',
                 prompt="Which statement about abstract classes in Java is true?",
                 options=['They can have constructors, which run when a subclass object is created', 'They cannot have constructors, because they cannot be instantiated', 'They must contain at least one abstract method', 'All their methods are implicitly public'],
                 answer=0,
                 explanation="An abstract class can declare constructors to initialise shared fields; subclasses call them through super. It may have zero abstract methods, and its methods follow normal access rules, so they are not implicitly public.",
                 hint='How would an abstract class set up its own fields?'),
            dict(id='challenge-oop-abstraction-and-interfaces-q4', kind='prediction', title='Implementing with no modifier',
                 prompt="interface Greeter { void greet(); } class Hi implements Greeter { void greet() { } } What happens?",
                 options=['It compiles normally', 'Compile error: greet must be public', 'It compiles, but greet is hidden outside the package'],
                 answer=1,
                 explanation="Greeter.greet is implicitly public. Hi.greet has package-private access, which is narrower, and an implementation cannot reduce visibility. Adding public fixes it.",
                 hint='What access does an interface method have by default?'),
            dict(id='challenge-oop-abstraction-and-interfaces-q5', kind='prediction', title='Clashing defaults',
                 prompt="Interfaces A and B both declare default void hello(). class C implements A, B and does not declare hello(). What happens?",
                 options=['A wins because it is listed first', 'It throws an exception when hello() is called', 'Both defaults run, one after the other', 'Compile error until C overrides hello() itself'],
                 answer=3,
                 explanation="Java refuses to guess between two equally specific defaults, so C fails to compile. C must override hello(), and it can delegate with A.super.hello() if it wants A's behaviour. Declaration order never decides, and the conflict is caught at compile time.",
                 hint='Does Java resolve this conflict at compile time or runtime?'),
        ],
    ),
    dict(
        id='guide-cs-fundamentals-oop-solid-principles', kind='guide', track='cs-fundamentals', subject='OOP',
        title='SOLID principles', order=6,
        summary="SOLID is five design guidelines that keep object-oriented code easy to change, extend and test.",
        sections=[
            dict(title='Single responsibility principle', text=(
                "SOLID is an acronym for five principles: single responsibility, open/closed, Liskov substitution, interface segregation and dependency inversion. "
                "They are guidelines for keeping classes small, focused and safe to change.\n\n"
                "The single responsibility principle says a class should have one reason to change. "
                "A useful reading is one group of people or one concern driving its changes. It does not mean a class may have only one method.\n\n"
                "Picture an Invoice class that calculates totals, saves itself to a database and renders a PDF. "
                "A tax rule change, a database migration and a new PDF layout would all edit the same file, and each change risks breaking the others. "
                "Splitting it into Invoice for the calculations, InvoiceRepository for storage and InvoicePrinter for output gives each piece a single reason to change."
            )),
            dict(title='Open/closed principle', text=(
                "Software entities should be open for extension but closed for modification. In practice, you should be able to add new behaviour by adding new code, not by editing working code.\n\n"
                "A classic violation is an AreaCalculator with a long if/else on the shape type: if circle, use this formula; if square, use that one. "
                "Every new shape forces you to reopen and edit the calculator, and to retest everything in it.\n\n"
                "The fix uses polymorphism. Give Shape an area() method and let each shape implement it. "
                "The calculator just sums shape.area() over the list. Adding a Triangle now means writing one new class, and the calculator never changes.\n\n"
                "Closed does not mean frozen forever. Bug fixes are still edits. The goal is that common, expected kinds of change arrive as extensions."
            )),
            dict(title='Liskov substitution principle', text=(
                "Objects of a subtype must be usable anywhere the base type is expected without breaking the program. "
                "A subclass may add behaviour, but it must keep the promises the parent makes.\n\n"
                "The textbook case is Square extends Rectangle. A rectangle lets you set width and height independently. "
                "To stay square, Square.setWidth also changes the height. Now code written for rectangles, which sets width to 5 and height to 4 and expects an area of 20, gets 16. "
                "Mathematically a square is a rectangle, but behaviourally this Square is not a substitute for this Rectangle.\n\n"
                "Warning signs of a violation include a subclass method that throws UnsupportedOperationException, one that silently does nothing, or callers that check instanceof before using the base type. "
                "Passing the is-a test in plain English is not enough; the subtype has to honour the parent's contract."
            )),
            dict(title='Interface segregation principle', text=(
                "Clients should not be forced to depend on methods they do not use. Prefer several small, focused interfaces over one large one.\n\n"
                "Suppose a Machine interface declares print, scan and fax. A basic printer must implement all three, so it ends up throwing exceptions from scan and fax. "
                "Every class that only wants to print now also depends on scanning and faxing, and a change to fax can force them to recompile or change.\n\n"
                "Splitting it into Printer, Scanner and FaxMachine lets the basic printer implement only Printer, while an office all-in-one implements all three. "
                "Each caller asks for exactly the capability it needs.\n\n"
                "Interface segregation and Liskov often show up together: a fat interface tempts classes to stub out methods, and stubbed methods break substitution."
            )),
            dict(title='Dependency inversion principle', text=(
                "High-level modules should not depend on low-level modules; both should depend on abstractions. Details should depend on abstractions, not the other way round.\n\n"
                "If OrderService creates new MySqlOrderRepository() inside itself, your business logic is welded to one database. "
                "You cannot test it without MySQL, and switching storage means editing the service.\n\n"
                "Instead, define an OrderRepository interface. OrderService receives one through its constructor and only knows the interface. "
                "MySqlOrderRepository implements it, and a test can pass an in-memory version.\n\n"
                "Do not confuse the principle with dependency injection. Dependency inversion is the design rule about which way dependencies point. "
                "Dependency injection is a technique, passing collaborators in from outside, and it is a common way to apply the principle, often with a framework such as Spring doing the wiring."
            )),
        ],
        keyPoints=[
            'Single responsibility: one reason to change, not one method.',
            'Open/closed: add behaviour through new classes, typically using polymorphism, instead of editing working code.',
            'Liskov substitution: a subtype must honour the base type\'s contract wherever the base type is used.',
            'Interface segregation: small focused interfaces so clients depend only on what they use.',
            'Dependency inversion: depend on abstractions; dependency injection is one way to achieve it.',
        ],
        challenges=[
            dict(id='challenge-oop-solid-principles-q1', kind='prediction', title='Busy invoice',
                 prompt="An Invoice class computes totals, saves itself to the database and generates a PDF. Which principle does it most directly violate?",
                 options=['Liskov substitution', 'Single responsibility', 'Interface segregation'],
                 answer=1,
                 explanation="The class has three unrelated reasons to change: pricing rules, storage and presentation. That is the definition of breaking single responsibility. Liskov is about subtypes, and interface segregation is about clients being forced to depend on unused methods, neither of which is the issue here.",
                 hint='Count how many different kinds of change would edit this class.'),
            dict(id='challenge-oop-solid-principles-q2', kind='prediction', title='Growing if/else',
                 prompt="An AreaCalculator uses if/else on each shape's type, and every new shape requires editing it. Which principle is violated?",
                 options=['Open/closed', 'Dependency inversion', 'Liskov substitution'],
                 answer=0,
                 explanation="Adding a feature forces you to modify existing, working code, which is what open/closed warns against. Giving each shape its own area() method lets new shapes be added as extensions. Dependency inversion and Liskov describe different problems.",
                 hint='Is new behaviour arriving as new code or as edits to old code?'),
            dict(id='challenge-oop-solid-principles-q3', kind='prediction', title='Square and rectangle',
                 prompt="Square extends Rectangle and setWidth also sets the height. Code that sets width 5 and height 4 on a Rectangle reference expects area 20 but gets 16 for a Square. Which principle is broken?",
                 options=['Single responsibility', 'Interface segregation', 'Liskov substitution'],
                 answer=2,
                 explanation="A Square cannot stand in for a Rectangle without changing the result callers rely on, which is exactly a Liskov violation. The class is not doing unrelated jobs, and no client is forced to depend on unused interface methods.",
                 hint='Can the subtype be used wherever the parent type is expected?'),
            dict(id='challenge-oop-solid-principles-q4', kind='prediction', title='Fat interface fix',
                 prompt="A Machine interface has print, scan and fax. BasicPrinter implements it and throws UnsupportedOperationException from scan and fax. What is the best fix?",
                 options=['Make scan and fax silently do nothing instead of throwing', 'Make BasicPrinter abstract', 'Add a canScan() method that callers check first', 'Split Machine into smaller interfaces such as Printer, Scanner and FaxMachine'],
                 answer=3,
                 explanation="The root problem is an interface that bundles unrelated capabilities, so interface segregation says to split it. Silent no-ops and capability flags hide the problem and still break substitution, and making BasicPrinter abstract means it can never be used at all.",
                 hint='Fix the interface, not the symptoms in the class.'),
            dict(id='challenge-oop-solid-principles-q5', kind='prediction', title='Following dependency inversion',
                 prompt="Which version of OrderService follows the dependency inversion principle?",
                 options=['It creates a new MySqlOrderRepository inside its constructor', 'It receives an OrderRepository interface through its constructor', 'It extends MySqlOrderRepository to reuse its save method'],
                 answer=1,
                 explanation="Depending on the OrderRepository abstraction means the high-level service no longer depends on a concrete database class, and any implementation can be passed in. Creating or extending MySqlOrderRepository ties the business logic directly to the low-level detail.",
                 hint='Which option leaves OrderService unaware of MySQL?'),
        ],
    ),
]
