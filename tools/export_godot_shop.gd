extends SceneTree
## One-time geometry transfer. Runtime uses the exported JSON, not Godot.
## godot --headless --path GODOT_PROJECT --script THIS_FILE -- OUTPUT.json
var output = {"meshes": [], "labels": [], "colliders": [], "lights": [], "nodes": {}}

func xyz(v: Vector3) -> Array:
	return [snapped(v.x, 0.000001), snapped(-v.z, 0.000001), snapped(v.y, 0.000001)]

func point(v: Vector3) -> Array:
	return xyz(v - Vector3(0, 0.2, 0))

func rgba(c: Color) -> Array:
	return [c.r, c.g, c.b, c.a]

func _initialize():
	call_deferred("export_scene")

func export_scene():
	var shop = load("res://scenes/shop/shop.tscn").instantiate()
	# Remove game scripts before entering the tree; export only the environment.
	for name in ["Player", "RepairJob"]:
		var child = shop.get_node_or_null(name)
		if child:
			shop.remove_child(child)
			child.free()
	root.add_child(shop)
	await process_frame
	await process_frame
	# Preserve the final playable Godot version's workbench material override.
	var finish = StandardMaterial3D.new()
	finish.albedo_color = Color("283e49")
	shop.get_node("Workshop/RepairWorkbench/RepairWorkbenchTop").material_override = finish
	walk(shop, shop)
	var args = OS.get_cmdline_user_args()
	var file = FileAccess.open(args[0], FileAccess.WRITE)
	file.store_string(JSON.stringify(output))
	print("SHOP EXPORT: ", output.meshes.size(), " surfaces, ", output.labels.size(), " labels, ", output.colliders.size(), " colliders")
	quit()

func export_mesh(mesh: Mesh, transform: Transform3D, path: String, override: Material = null):
	for i in mesh.get_surface_count():
		var arr = mesh.surface_get_arrays(i)
		if arr.is_empty(): continue
		var mat = override if override else mesh.surface_get_material(i)
		var color = Color.WHITE
		var emission = false
		if mat is BaseMaterial3D:
			color = mat.albedo_color
			emission = mat.emission_enabled
		var vertices = []
		var normals = []
		for v in arr[Mesh.ARRAY_VERTEX]: vertices.append(point(transform * v))
		for n in arr[Mesh.ARRAY_NORMAL]: normals.append(xyz((transform.basis.inverse().transposed() * n).normalized()))
		var indices = []
		if arr[Mesh.ARRAY_INDEX] != null:
			for index in arr[Mesh.ARRAY_INDEX]: indices.append(index)
		if indices.is_empty():
			for index in vertices.size(): indices.append(index)
		output.meshes.append({"name": path, "vertices": vertices, "normals": normals, "indices": indices, "color": rgba(color), "emission": emission})

func walk(node: Node, shop: Node):
	var path = str(shop.get_path_to(node))
	if node is Node3D:
		output.nodes[path] = {"position": point(node.global_position), "right": xyz(node.global_basis.x), "up": xyz(node.global_basis.y), "front": xyz(node.global_basis.z)}
	if node is CSGShape3D and node.is_root_shape():
		var meshes = node.get_meshes()
		if meshes.size() == 2:
			export_mesh(meshes[1], node.global_transform, path)
		if node is CSGBox3D and node.use_collision:
			export_box(node.global_transform, node.size, path)
	elif node is MeshInstance3D and node.mesh and node.is_visible_in_tree():
		export_mesh(node.mesh, node.global_transform, path, node.material_override)
	elif node is Label3D:
		output.labels.append({"name": path, "position": point(node.global_position), "front": xyz(node.global_basis.z), "text": node.text, "size": node.font_size * node.pixel_size, "color": rgba(node.modulate)})
	elif node is CollisionShape3D and not node.disabled and node.shape is BoxShape3D:
		export_box(node.global_transform, node.shape.size, path)
	elif node is Light3D:
		output.lights.append({"name": path, "type": node.get_class(), "position": point(node.global_position), "direction": xyz(-node.global_basis.z), "color": rgba(node.light_color), "energy": node.light_energy})
	for child in node.get_children(): walk(child, shop)

func export_box(transform: Transform3D, size: Vector3, path: String):
	var points = []
	for x in [-0.5, 0.5]:
		for y in [-0.5, 0.5]:
			for z in [-0.5, 0.5]: points.append(point(transform * (size * Vector3(x, y, z))))
	output.colliders.append({"name": path, "points": points})
