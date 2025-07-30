You’re describing a very common design tension in C++:

You have a base class pointer (Car_Model_Base*) that refers to an object of derived type (Car_Model), and you want to access members only defined in the derived type, like getDestination() — but without modifying the base class.

This is type-safe and doable, as long as:
	1.	You’re certain the object is actually a Car_Model.
	2.	You’re willing to cast appropriately.

⸻

✅ Solution: Use dynamic_cast

std::unordered_map<int, Car_Model_Base*> model_map = car_manager.getModels();

for (const auto& [id, base_ptr] : model_map) {
    Car_Model* model = dynamic_cast<Car_Model*>(base_ptr);
    if (model) {
        auto dest = model->getDestination();
        // Do something with dest
    } else {
        // Optional: warn or handle unexpected type
    }
}

✅ Why this works:
	•	dynamic_cast<Car_Model*>(base_ptr) will return a valid pointer if and only if the object is actually a Car_Model.
	•	Otherwise, it returns nullptr, allowing you to safely check.
	•	Requires that Car_Model_Base has at least one virtual function (often a virtual destructor).

⸻

🧱 Why Not Just Add It to the Base Class?

You said:

I don’t want to add destination to Car_Model_Base.

That makes sense if destination is not semantically appropriate for all derived types, or you’re maintaining a clean separation of concerns. This is a good design instinct.

⸻

🧼 Optional Cleanup

If most of your objects in the map are of type Car_Model, and the cast is almost always successful, you might:
	•	Encapsulate the cast logic in a helper function.
	•	Log or assert unexpected types.

Example helper:

Car_Model* try_cast_to_model(Car_Model_Base* base) {
    auto model = dynamic_cast<Car_Model*>(base);
    if (!model) {
        std::cerr << "Unexpected model type. Ignored.\n";
    }
    return model;
}


⸻

⚠️ Don’t Use static_cast Here

Car_Model* model = static_cast<Car_Model*>(base_ptr); // ⚠️ Undefined behavior if wrong type!

	•	static_cast doesn’t check the type at runtime.
	•	Use only if you’re 100% sure the type is correct (e.g., from a sealed framework or factory you control).

⸻

🧠 Design Tip

If this situation comes up frequently, and destination is really meaningful only to some derived types:
	•	Consider adding a virtual function to the base class like virtual std::optional<Destination> getOptionalDestination() const { return std::nullopt; }
	•	That lets you cleanly access optional features without leaking type-specific logic into the caller.

Would you like to explore that optional virtual design pattern as a safer alternative?