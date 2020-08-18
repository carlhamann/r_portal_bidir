/*
    Lightmetrica - Copyright (c) 2019 Hisanari Otsu
    Distributed under MIT license. See LICENSE file for details.
*/

#include <lm/core.h>
#include <lm/renderer.h>
#include <lm/scheduler.h>
#include <lm/mesh.h>
#include <lm/scene.h>
#include <lm/film.h>
#include <lm/timer.h>
#include <lm/path.h>
#include <lm/bidir.h>
#include "portal.h"
#include "debug.h"

LM_NAMESPACE_BEGIN(LM_NAMESPACE)

LM_NAMESPACE_BEGIN(portalbidir)

// Sample an intermediate subpath of length 1 from the portal.
// Conventionally, we assume the normal of the portal mesh is facing toward the outside.
// That is, vs[0] connects to the light subpath and vs[1] connects to the eye subpath.
Path sample_intermediate_subpath(Rng& rng, const Scene* scene, const Portal& portal) {
	Path path;

	// Sample a ray from the portal
	Ray portal_ray = portal.sample_ray(rng);
	{
		// 1. Intersection to next surface
		const auto hit = scene->intersect(portal_ray);
		if (!hit) {
			return {};
		}
		// Sample component & add a vertex
		const auto s_comp = path::sample_component(rng, scene, *hit, -portal_ray.d);
		path.vs.push_back({ *hit, s_comp.comp });
	}
	{
		// 2. Intersection to next surface in opposite direction
		const auto hit = scene->intersect({ portal_ray.o, -portal_ray.d });
		if (!hit) {
			return {};
		}
		// Sample component & add a vertex
		const auto s_comp = path::sample_component(rng, scene, *hit, portal_ray.d);
		path.vs.push_back({ *hit, s_comp.comp });
	}

	return path;
}

// paths longer than 1
Path sample_intermediate_subpath_long(Rng& rng, const Scene* scene, const Portal& portal, int max_verts) {
	Path path;

	// Subpaths in both directions
	Path subpathL;
	Path subpathE;

	// Sample a ray from the portal
	Ray portal_ray = portal.sample_ray(rng);
	{
		// 1.1 Intersection to next surface
		const auto hit = scene->intersect(portal_ray);
		if (!hit) {
			return {};
		}
		// Sample component & add a vertex
		const auto s_comp = path::sample_component(rng, scene, *hit, -portal_ray.d);
		//path.vs.push_back({ *hit, s_comp.comp });

		// 1.2 Sample subpath in light direction
		// We initialize the inital vertex with the previous hit point
		subpathL.vs.push_back({ *hit, s_comp.comp });
		path::sample_subpath_from_endpoint(rng, subpathL, scene, max_verts, TransDir::EL);
	}
	{
		// 2.1 Intersection to next surface in opposite direction
		const auto hit = scene->intersect({ portal_ray.o, -portal_ray.d });
		if (!hit) {
			return {};
		}
		// Sample component & add a vertex
		const auto s_comp = path::sample_component(rng, scene, *hit, portal_ray.d);
		//path.vs.push_back({ *hit, s_comp.comp });

		// 1.2 Sample subpath in light direction
		// We initialize the inital vertex with the previous hit point
		subpathE.vs.push_back({ *hit, s_comp.comp });
		path::sample_subpath_from_endpoint(rng, subpathE, scene, max_verts, TransDir::LE);
	}

	// Now compose the final intermediate subpath:
	// We choose about half from both sub-subpaths if possible
	int nL = subpathL.num_verts();
	int nE = subpathE.num_verts();
	int numL = 0;
	int numE = 0;
	if (nL > nE)
	{
		numE = glm::min(max_verts / 2, nE);
		numL = glm::min(max_verts - numE, nL);
	}
	else
	{
		numL = glm::min(max_verts / 2, nL);
		numE = glm::min(max_verts - numL, nE);
	}

	// First light subpath (reverse)
	path.vs.insert(path.vs.end(), subpathL.vs.rend() - numL, subpathL.vs.rend());

	// Then eye subpath
	path.vs.insert(path.vs.end(), subpathE.vs.begin(), subpathE.vs.begin() + numE);

	return path;
}

// Connect subpaths (light, eye, intermediate) and construct a full path
std::optional<Path> connect_subpaths(const Scene* scene, const Path& subpathL, const Path& subpathE, const Path& subpathI, int s, int t) {
    assert(s >= 0 && t >= 0);
    assert(!(s == 0 && t == 0));
    assert(subpathI.num_verts() == 2);
    
    Path path;

    if (s == 0) {
        // Case: No light subpath, single connection
        const auto& vE = subpathE.vs[t-1];
        const auto& vIE = subpathI.vs[1];
        
        // Check invalid connection
        if (vE.sp.geom.infinite || vIE.sp.geom.infinite) {
            return {};
        }
        if (!scene->visible(vE.sp, vIE.sp)) {
            return {};
        }
        
        // Copy intermediate subpath
        path.vs.insert(path.vs.end(), subpathI.vs.begin(), subpathI.vs.begin() + 2);
        
        // Copy eye subpath
        path.vs.insert(path.vs.end(), subpathE.vs.rend() - t, subpathE.vs.rend());
    }
    else if (t == 0) {
        // Case: No eye subpath, single connection
        const auto& vL = subpathL.vs[s-1];
        const auto& vIL = subpathI.vs[0];
        
        // Check invalid connection
        if (vL.sp.geom.infinite || vIL.sp.geom.infinite) {
            return {};
        }
        if (!scene->visible(vL.sp, vIL.sp)) {
            return {};
        }

        // Copy light subpath
        path.vs.insert(path.vs.end(), subpathL.vs.begin(), subpathL.vs.begin() + s);

        // Copy intermediate subpath
        path.vs.insert(path.vs.end(), subpathI.vs.begin(), subpathI.vs.begin() + 2);
    }
    else {
        // Case: Other cases, double connections
        const auto& vL = subpathL.vs[s-1];
        const auto& vE = subpathE.vs[t-1];
        const auto& vIL = subpathI.vs[0];
        const auto& vIE = subpathI.vs[1];
        if (vL.sp.geom.infinite || vE.sp.geom.infinite || vIL.sp.geom.infinite || vIE.sp.geom.infinite) {
            return {};
        }
        if (!scene->visible(vL.sp, vIL.sp) || !scene->visible(vIE.sp, vE.sp)) {
            return {};
        }
        path.vs.insert(path.vs.end(), subpathL.vs.begin(), subpathL.vs.begin() + s);
        path.vs.insert(path.vs.end(), subpathI.vs.begin(), subpathI.vs.begin() + 2);
        path.vs.insert(path.vs.end(), subpathE.vs.rend() - t, subpathE.vs.rend());
    }
    
    // Check endpoint types
    // We assume the initial vertex of eye subpath is always camera endpoint.
    // That is scene.is_camera(vE) is always true.
    auto& vL = path.vs.front();
    if (!scene->is_light(vL.sp)) {
        return {};
    }
    auto& vE = path.vs.back();
    if (!scene->is_camera(vE.sp)) {
        return {};
    }

    // Update the endpoint types
    vL.sp = vL.sp.as_type(SceneInteraction::LightEndpoint);
    vE.sp = vE.sp.as_type(SceneInteraction::CameraEndpoint);
    
    return path;
}

// Version for inter renderer
std::optional<Path> connect_subpaths_inter(const Scene* scene, const Path& subpathL, const Path& subpathE, const Path& subpathI, int s, int t) {
	assert(s >= 0 && t >= 0);
	//assert(!(s == 0 && t == 0);		// Only intermediate subpath could be inserted
	assert(subpathI.num_verts() == 2);

	Path path;

	if (s == 0 && t == 0)
	{
		// Case: Only intermediate subpath
		const auto& vIL = subpathI.vs[0];
		const auto& vIE = subpathI.vs[1];

		if (vIL.sp.geom.infinite || vIE.sp.geom.infinite) {
			return {};
		}

		// Just intermediate subpath
		path.vs.insert(path.vs.end(), subpathI.vs.begin(), subpathI.vs.begin() + 2);
	}
	else if (s == 0) {
		// Case: No light subpath, single connection
		const auto& vE = subpathE.vs[t - 1];
		const auto& vIE = subpathI.vs[1];

		// Check invalid connection
		if (vE.sp.geom.infinite || vIE.sp.geom.infinite) {
			return {};
		}
		if (!scene->visible(vE.sp, vIE.sp)) {
			return {};
		}

		// Copy intermediate subpath
		path.vs.insert(path.vs.end(), subpathI.vs.begin(), subpathI.vs.begin() + 2);

		// Copy eye subpath
		path.vs.insert(path.vs.end(), subpathE.vs.rend() - t, subpathE.vs.rend());
	}
	else if (t == 0) {
		// Case: No eye subpath, single connection
		const auto& vL = subpathL.vs[s - 1];
		const auto& vIL = subpathI.vs[0];

		// Check invalid connection
		if (vL.sp.geom.infinite || vIL.sp.geom.infinite) {
			return {};
		}
		if (!scene->visible(vL.sp, vIL.sp)) {
			return {};
		}

		// Copy light subpath
		path.vs.insert(path.vs.end(), subpathL.vs.begin(), subpathL.vs.begin() + s);

		// Copy intermediate subpath
		path.vs.insert(path.vs.end(), subpathI.vs.begin(), subpathI.vs.begin() + 2);
	}
	else {
		// Case: Other cases, double connections
		const auto& vL = subpathL.vs[s - 1];
		const auto& vE = subpathE.vs[t - 1];
		const auto& vIL = subpathI.vs[0];
		const auto& vIE = subpathI.vs[1];
		if (vL.sp.geom.infinite || vE.sp.geom.infinite || vIL.sp.geom.infinite || vIE.sp.geom.infinite) {
			return {};
		}
		if (!scene->visible(vL.sp, vIL.sp) || !scene->visible(vIE.sp, vE.sp)) {
			return {};
		}
		path.vs.insert(path.vs.end(), subpathL.vs.begin(), subpathL.vs.begin() + s);
		path.vs.insert(path.vs.end(), subpathI.vs.begin(), subpathI.vs.begin() + 2);
		path.vs.insert(path.vs.end(), subpathE.vs.rend() - t, subpathE.vs.rend());
	}

	// Check endpoint types
	// We assume the initial vertex of eye subpath is always camera endpoint.
	// That is scene.is_camera(vE) is always true.
	auto& vL = path.vs.front();
	if (!scene->is_light(vL.sp)) {
		return {};
	}
	auto& vE = path.vs.back();
	if (!scene->is_camera(vE.sp)) {
		return {};
	}

	// Update the endpoint types
	vL.sp = vL.sp.as_type(SceneInteraction::LightEndpoint);
	vE.sp = vE.sp.as_type(SceneInteraction::CameraEndpoint);

	return path;
}

// Longer intermediate subpath
std::optional<Path> connect_subpaths_long(const Scene* scene, const Path& subpathL, const Path& subpathE, const Path& subpathI, int s, int s2, int t2, int t) {
	assert(s >= 0 && s2 >= 0 && t2 >= 0 t >= 0);
	assert(!(s == 0 && s2 == 0 & t2 == 0 && t == 0));

	Path path;

	
	if (s == 0 && t == 0 && s2 == 0)
	{
		// Case: t' > 0
		const auto& vIL = subpathI.vs[0];
		const auto& vIE = subpathI.vs[t2 - 1];

		if (vIL.sp.geom.infinite || vIE.sp.geom.infinite) {
			return {};
		}

		// Just (eye-)intermediate subpath
		path.vs.insert(path.vs.end(), subpathI.vs.begin(), subpathI.vs.begin() + t2);
	}
	else if (s == 0 && t == 0 && t2 == 0)
	{
		// Case: s' > 0
		const auto& vIL = subpathI.vs[0];
		const auto& vIE = subpathI.vs[s2 - 1];

		if (vIL.sp.geom.infinite || vIE.sp.geom.infinite) {
			return {};
		}

		// Just (light-)intermediate subpath (reverse)
		path.vs.insert(path.vs.end(), subpathI.vs.rend() - s2, subpathI.vs.rend());
	}
	else if (s == 0 && s2 == 0 && t2 == 0)
	{
		// Case: t > 0
		const auto& vL = subpathE.vs[t - 1];

		if (vL.sp.geom.infinite) {
			return {};
		}

		// Just eye subpath (reverse)
		path.vs.insert(path.vs.end(), subpathE.vs.rend() - t, subpathE.vs.rend());
	}
	else if (t == 0 && s2 == 0 && t2 == 0)
	{
		// Case: s > 0
		const auto& vE = subpathE.vs[s - 1];

		if (vE.sp.geom.infinite) {
			return {};
		}

		// Just light subpath
		path.vs.insert(path.vs.end(), subpathL.vs.begin(), subpathL.vs.begin() + s);
	}



	if (s == 0 && t == 0)
	{
		// Case: Only intermediate subpath
		const auto& vIL = subpathI.vs[0];
		const auto& vIE = subpathI.vs[1];

		if (vIL.sp.geom.infinite || vIE.sp.geom.infinite) {
			return {};
		}

		// Just intermediate subpath
		path.vs.insert(path.vs.end(), subpathI.vs.begin(), subpathI.vs.begin() + 2);
	}
	else if (s == 0) {
		// Case: No light subpath, single connection
		const auto& vE = subpathE.vs[t - 1];
		const auto& vIE = subpathI.vs[1];

		// Check invalid connection
		if (vE.sp.geom.infinite || vIE.sp.geom.infinite) {
			return {};
		}
		if (!scene->visible(vE.sp, vIE.sp)) {
			return {};
		}

		// Copy intermediate subpath
		path.vs.insert(path.vs.end(), subpathI.vs.begin(), subpathI.vs.begin() + 2);

		// Copy eye subpath
		path.vs.insert(path.vs.end(), subpathE.vs.rend() - t, subpathE.vs.rend());
	}
	else if (t == 0) {
		// Case: No eye subpath, single connection
		const auto& vL = subpathL.vs[s - 1];
		const auto& vIL = subpathI.vs[0];

		// Check invalid connection
		if (vL.sp.geom.infinite || vIL.sp.geom.infinite) {
			return {};
		}
		if (!scene->visible(vL.sp, vIL.sp)) {
			return {};
		}

		// Copy light subpath
		path.vs.insert(path.vs.end(), subpathL.vs.begin(), subpathL.vs.begin() + s);

		// Copy intermediate subpath
		path.vs.insert(path.vs.end(), subpathI.vs.begin(), subpathI.vs.begin() + 2);
	}
	else {
		// Case: Other cases, double connections
		const auto& vL = subpathL.vs[s - 1];
		const auto& vE = subpathE.vs[t - 1];
		const auto& vIL = subpathI.vs[0];
		const auto& vIE = subpathI.vs[1];
		if (vL.sp.geom.infinite || vE.sp.geom.infinite || vIL.sp.geom.infinite || vIE.sp.geom.infinite) {
			return {};
		}
		if (!scene->visible(vL.sp, vIL.sp) || !scene->visible(vIE.sp, vE.sp)) {
			return {};
		}
		path.vs.insert(path.vs.end(), subpathL.vs.begin(), subpathL.vs.begin() + s);
		path.vs.insert(path.vs.end(), subpathI.vs.begin(), subpathI.vs.begin() + 2);
		path.vs.insert(path.vs.end(), subpathE.vs.rend() - t, subpathE.vs.rend());
	}

	// Check endpoint types
	// We assume the initial vertex of eye subpath is always camera endpoint.
	// That is scene.is_camera(vE) is always true.
	auto& vL = path.vs.front();
	if (!scene->is_light(vL.sp)) {
		return {};
	}
	auto& vE = path.vs.back();
	if (!scene->is_camera(vE.sp)) {
		return {};
	}

	// Update the endpoint types
	vL.sp = vL.sp.as_type(SceneInteraction::LightEndpoint);
	vE.sp = vE.sp.as_type(SceneInteraction::CameraEndpoint);

	return path;
}

// Evaluate connection term
Vec3 eval_connection_term(const Path& path, const Scene* scene, int s) {
    const int n = path.num_verts();
    const int t = n - s - 2;

    // --  : connection
    // ... : unrelated vertices

    // Helper function to compute related terms for connections.
    // Note that vL or vE might not the end of the light/eye subpath.
    // j: index of the vertex with connection from endpoint
    // vL and vE must not be nullptr.
    const auto connection_term = [&](int j, TransDir trans_dir) -> Vec3 {
        // Index of vL from L
        const int i = trans_dir == TransDir::LE ? j : path.num_verts()-2-j;

        // ... vL_prev vL -- vE vE_prev ...
        const auto* vL = path.vertex_at(i, TransDir::LE);
        const auto* vE = path.vertex_at(i+1, TransDir::LE);
        const auto* vL_prev = path.vertex_at(i-1, TransDir::LE);
        const auto* vE_prev = path.vertex_at(i+2, TransDir::LE);

        // Computer terms
        const auto fsL = path::eval_contrb_direction(
            scene, vL->sp, path.direction(vL, vL_prev), path.direction(vL, vE), vL->comp, TransDir::LE, true);
        const auto fsE = path::eval_contrb_direction(
            scene, vE->sp, path.direction(vE, vE_prev), path.direction(vE, vL), vE->comp, TransDir::EL, true);
        const auto G = surface::geometry_term(vL->sp.geom, vE->sp.geom);
        
        return fsL * G * fsE;
    };

    Vec3 cst{};
    if (s == 0) {
        // vpL vpE -- vE vE_prev ...
        const auto* vpL = path.vertex_at(0, TransDir::LE);
        const auto* vpE = path.vertex_at(1, TransDir::LE);
        const auto Le = path::eval_contrb_direction(
            scene, vpL->sp, {}, path.direction(vpL, vpE), vpL->comp, TransDir::LE, true);
        const auto G = surface::geometry_term(vpL->sp.geom, vpE->sp.geom);
        const auto conn = connection_term(1, TransDir::LE);
        cst = Le * G * conn;
    }
    else if (t == 0) {
        // ... vL_prev vL -- vpL vpE
        const auto* vpL = path.vertex_at(1, TransDir::EL);
        const auto* vpE = path.vertex_at(0, TransDir::EL);
        const auto We = path::eval_contrb_direction(
            scene, vpE->sp, {}, path.direction(vpE, vpL), vpE->comp, TransDir::EL, true);
        const auto G = surface::geometry_term(vpE->sp.geom, vpL->sp.geom);
        const auto conn = connection_term(1, TransDir::EL);
        cst = We * G * conn;
    }
    else {
        // ... vL_prev vL -- vpL vpE -- vE vE_prev ...
        const auto* vpL = path.vertex_at(s, TransDir::LE);
        const auto* vpE = path.vertex_at(t, TransDir::EL);
        const auto G = surface::geometry_term(vpL->sp.geom, vpE->sp.geom);
        const auto connL = connection_term(s-1, TransDir::LE);
        const auto connE = connection_term(t-1, TransDir::EL);
        cst = connL * G * connE;
    }

    return cst;
}

// Evaluate connection term
Vec3 eval_connection_term_inter(const Path& path, const Scene* scene, int s) {
	const int n = path.num_verts();
	const int t = n - s - 2;

	// --  : connection
	// ... : unrelated vertices

	// Helper function to compute related terms for connections.
	// Note that vL or vE might not the end of the light/eye subpath.
	// j: index of the vertex with connection from endpoint
	// vL and vE must not be nullptr.
	const auto connection_term = [&](int j, TransDir trans_dir) -> Vec3 {
		// Index of vL from L
		const int i = trans_dir == TransDir::LE ? j : path.num_verts() - 2 - j;

		// ... vL_prev vL -- vE vE_prev ...
		const auto* vL = path.vertex_at(i, TransDir::LE);
		const auto* vE = path.vertex_at(i + 1, TransDir::LE);
		const auto* vL_prev = path.vertex_at(i - 1, TransDir::LE);
		const auto* vE_prev = path.vertex_at(i + 2, TransDir::LE);

		// Compute terms
		const auto fsL = path::eval_contrb_direction(
			scene, vL->sp, path.direction(vL, vL_prev), path.direction(vL, vE), vL->comp, TransDir::LE, true);
		const auto fsE = path::eval_contrb_direction(
			scene, vE->sp, path.direction(vE, vE_prev), path.direction(vE, vL), vE->comp, TransDir::EL, true);
		const auto G = surface::geometry_term(vL->sp.geom, vE->sp.geom);

		return fsL * G * fsE;
	};

	Vec3 cst{};

	if (s == 0 && t == 0)
	{
		// vpL vpE
		const auto* vpL = path.vertex_at(0, TransDir::LE);
		const auto* vpE = path.vertex_at(1, TransDir::LE);
		const auto Le = path::eval_contrb_direction(
			scene, vpL->sp, {}, path.direction(vpL, vpE), vpL->comp, TransDir::LE, true);
		const auto G = surface::geometry_term(vpL->sp.geom, vpE->sp.geom);
		cst = Le * G;
	}
	else if (s == 0) {
		// vpL vpE -- vE vE_prev ...
		const auto* vpL = path.vertex_at(0, TransDir::LE);
		const auto* vpE = path.vertex_at(1, TransDir::LE);
		const auto Le = path::eval_contrb_direction(
			scene, vpL->sp, {}, path.direction(vpL, vpE), vpL->comp, TransDir::LE, true);
		const auto G = surface::geometry_term(vpL->sp.geom, vpE->sp.geom);
		const auto conn = connection_term(1, TransDir::LE);
		cst = Le * G * conn;
	}
	else if (t == 0) {
		// ... vL_prev vL -- vpL vpE
		const auto* vpL = path.vertex_at(1, TransDir::EL);
		const auto* vpE = path.vertex_at(0, TransDir::EL);
		const auto We = path::eval_contrb_direction(
			scene, vpE->sp, {}, path.direction(vpE, vpL), vpE->comp, TransDir::EL, true);
		const auto G = surface::geometry_term(vpE->sp.geom, vpL->sp.geom);
		const auto conn = connection_term(1, TransDir::EL);
		cst = We * G * conn;
	}
	else {
		// ... vL_prev vL -- vpL vpE -- vE vE_prev ...
		const auto* vpL = path.vertex_at(s, TransDir::LE);
		const auto* vpE = path.vertex_at(t, TransDir::EL);
		const auto G = surface::geometry_term(vpL->sp.geom, vpE->sp.geom);
		const auto connL = connection_term(s - 1, TransDir::LE);
		const auto connE = connection_term(t - 1, TransDir::EL);
		cst = connL * G * connE;
	}

	return cst;
}

// Evaluate evaluate contribution function
Vec3 eval_measurement_contrb(const Path& path, const Scene* scene, int s) {
    const int n = path.num_verts();
    const int t = n - s - 2;
    
    // Compute contribution for subpath (l = s or t)
    const auto eval_contrb_subpath = [&](int l, TransDir trans_dir) -> Vec3 {
        if (l == 0) {
            return Vec3(1_f);
        }
        auto f_prod = Vec3(1_f);
        for (int i = 0; i < l - 1; i++) {
            const auto* v = path.vertex_at(i, trans_dir);
            const auto* v_prev = path.vertex_at(i - 1, trans_dir);
            const auto* v_next = path.vertex_at(i + 1, trans_dir);
            const auto wi = path.direction(v, v_prev);
            const auto wo = path.direction(v, v_next);
            f_prod *= path::eval_contrb_direction(scene, v->sp, wi, wo, v->comp, trans_dir, false);
            f_prod *= surface::geometry_term(v->sp.geom, v_next->sp.geom);
        }
        return f_prod;
    };

    // Product of terms
    const auto f_prod_L = eval_contrb_subpath(s, TransDir::LE);
    const auto f_prod_E = eval_contrb_subpath(t, TransDir::EL);

    // Connection term
    const auto cst = eval_connection_term(path, scene, s);

    return f_prod_L * cst * f_prod_E;
}

// Evaluate evaluate contribution function
Vec3 eval_measurement_contrb_inter(const Path& path, const Scene* scene, int s) {
	const int n = path.num_verts();
	const int t = n - s - 2;

	// Compute contribution for subpath (l = s or t)
	const auto eval_contrb_subpath = [&](int l, TransDir trans_dir) -> Vec3 {
		if (l == 0) {
			return Vec3(1_f);
		}
		auto f_prod = Vec3(1_f);
		for (int i = 0; i < l - 1; i++) {
			const auto* v = path.vertex_at(i, trans_dir);
			const auto* v_prev = path.vertex_at(i - 1, trans_dir);
			const auto* v_next = path.vertex_at(i + 1, trans_dir);
			const auto wi = path.direction(v, v_prev);
			const auto wo = path.direction(v, v_next);
			f_prod *= path::eval_contrb_direction(scene, v->sp, wi, wo, v->comp, trans_dir, false);
			f_prod *= surface::geometry_term(v->sp.geom, v_next->sp.geom);
		}
		return f_prod;
	};

	// Product of terms
	const auto f_prod_L = eval_contrb_subpath(s, TransDir::LE);
	const auto f_prod_E = eval_contrb_subpath(t, TransDir::EL);

	// Connection term
	const auto cst = eval_connection_term_inter(path, scene, s);

	return f_prod_L * cst * f_prod_E;
}


// Check if the path is samplable by the given strategy
bool is_samplable(const Path& path, const Scene* scene, const Portal& portal, int s) {
    const int n = path.num_verts();
    const int t = n - s - 2;

    // Check if the edge vs[s] vs[s+1] intersects with the portal.
    // Otherwise, the path cannot be sampled since there is no way to sample the intermediate path.
    {
        // ... vpL vpE ...
        const auto* vpL = path.vertex_at(s, TransDir::LE);
        const auto* vpE = path.vertex_at(t, TransDir::EL);
        if (!portal.intersect_with_segment(vpE->sp.geom, vpL->sp.geom)) {
            return false;
        }
    }

    // Check if the connection is samplable
    // j: index of the vertex with connection from endpoint
    const auto is_samplable_connection = [&](int j, TransDir trans_dir) -> bool {
        // Index of vL from L
        const int i = trans_dir == TransDir::LE ? j : path.num_verts()-2-j;

        // ... vL -- vE ...
        const auto* vL = path.vertex_at(i, TransDir::LE);
        const auto* vE = path.vertex_at(i+1, TransDir::LE);

        if (i == 0 && !path::is_connectable_endpoint(scene, vL->sp)) {
            // Not samplebale if the endpoint is not connectable
            return false;
        }
        else if (i == n-1 && !path::is_connectable_endpoint(scene, vE->sp)) {
            // Not samplebale if the endpoint is not connectable
            return false;
        }
        // Not samplable if either vL or vE is specular component
        if (path::is_specular_component(scene, vL->sp, vL->comp) ||
            path::is_specular_component(scene, vE->sp, vE->comp)) {
            return false;
        }

        return true;
    };

    // Check if the endpoint is samplable
    const auto is_samplable_endpoint = [&](TransDir trans_dir) -> bool {
        const auto* v_ep = path.vertex_at(0, trans_dir);
        return !v_ep->sp.geom.degenerated &&
               !path::is_specular_component(scene, v_ep->sp, v_ep->comp);
    };

    if (s == 0) {
        // vpL vpE -- vE ...
        return is_samplable_endpoint(TransDir::LE) &&
               is_samplable_connection(1, TransDir::LE);
    }
    else if (t == 0) {
        // ... vL -- vpL vpE   
        return is_samplable_endpoint(TransDir::EL) &&
               is_samplable_connection(1, TransDir::EL);
    }
    else {
        // ... vL -- vpL vpE -- vE ...  
        return is_samplable_connection(s-1, TransDir::LE) &&
               is_samplable_connection(t-1, TransDir::EL);
    }
}

// Evaluate path PDF
Float pdf(const Path& path, const Scene* scene, const Portal& portal, int s) {
    const int n = path.num_verts();
    const int t = n - s - 2;

    // If the path is not samplable by the strategy, return zero.
    if (!is_samplable(path, scene, portal, s)) {
        return 0_f;
    }

    // Compute a product of local PDFs
    const auto pdf_subpath = [&](int l, TransDir trans_dir) -> Float {
        if (l == 0) {
            return 1_f;
        }

        int i = 0;
        Float p = 0_f;
        const auto* v0 = path.vertex_at(0, trans_dir);
        if (path::is_connectable_endpoint(scene, v0->sp)) {
            const auto pA = path::pdf_position(scene, v0->sp);
            const auto p_comp = path::pdf_component(scene, v0->sp, {}, v0->comp);
            p = pA * p_comp;
        }
        else {
            const auto* v1 = path.vertex_at(1, trans_dir);
            const auto d01 = path.direction(v0, v1);
            const auto p_ray = path::pdf_primary_ray(scene, v0->sp, d01, false);
            const auto p_comp_v0 = path::pdf_component(scene, v0->sp, {}, v0->comp);
            const auto p_comp_v1 = path::pdf_component(scene, v1->sp, -d01, v1->comp);
            p = surface::convert_pdf_to_area(p_ray, v0->sp.geom, v1->sp.geom) * p_comp_v0 * p_comp_v1;
            i++;
        }

        for (; i < l - 1; i++) {
            const auto* v      = path.vertex_at(i,   trans_dir);
            const auto* v_prev = path.vertex_at(i-1, trans_dir);
            const auto* v_next = path.vertex_at(i+1, trans_dir);
            const auto wi = path.direction(v, v_prev);
            const auto wo = path.direction(v, v_next);
            const auto p_comp = path::pdf_component(scene, v_next->sp, -wo, v_next->comp);
            const auto p_projSA = path::pdf_direction(scene, v->sp, wi, wo, v->comp, false);
            p *= (p_comp * surface::convert_pdf_to_area(p_projSA, v->sp.geom, v_next->sp.geom));
        }

        return p;
    };

    // Compute PDF for sampling intermediate subpath
    const auto pdf_intermediate_subpath = [&]() -> Float {
        // Jacobian to convert to the product area measure around xpL and xpE is simply G(xpL,xpE).
        // This should be discussed in the paper. See my submission of the portal-mlt paper.
        const auto* vpL = path.vertex_at(s, TransDir::LE);
        const auto* vpE = path.vertex_at(t, TransDir::EL);
        const auto dLE = path.direction(vpL, vpE);
        const auto dEL = -dLE;
        const auto pApD = portal.pdf_ray(dEL);
        const auto pA2 = surface::convert_pdf_to_area(pApD, vpL->sp.geom, vpE->sp.geom);
        const auto p_compL = path::pdf_component(scene, vpL->sp, dLE, vpL->comp);
        const auto p_compE = path::pdf_component(scene, vpE->sp, dEL, vpE->comp);
        return pA2 * p_compL * p_compE;
    };

    // Compute product of local PDFs for each subpath
    const auto pL = pdf_subpath(s, TransDir::LE);
    const auto pI = pdf_intermediate_subpath();
    const auto pE = pdf_subpath(t, TransDir::EL);

    return pL * pI * pE;
}

// Evaluate MIS weight
Float eval_mis_weight(const Path& path, const Scene* scene, const Portal& portal, int s) {
    const int n = path.num_verts();
    const int t = n - s - 2;

    const auto ps = pdf(path, scene, portal, s);
    assert(ps > 0_f);

    Float inv_w = 0_f;
    for (int s2 = 0; s2 <= n-2; s2++) {
        const auto pi = pdf(path, scene, portal, s2);
        if (pi == 0_f) {
            continue;
        }
        const auto r = pi / ps;
        inv_w += r * r;
    }

    return 1_f / inv_w;
}

LM_NAMESPACE_END(portalbidir)

// ------------------------------------------------------------------------------------------------

// Enable to output per-strategy films
#define BDPT_PORTAL_PER_STRATEGY_FILM 1
// Poll sampled paths (used for visual debugging)
#define BDPT_PORTAL_POLL_PATHS 1

/*
    Implements portal-based BDPT (simplified version).
    Simplifications:

      - Number of portals is limited to one.
      - Only consider the strategies using portals.
      - Portal edge (path edge passing through a portal) is limited to length 1.
      - Fixed path length.
*/
class Renderer_Portal_BDPT_Fixed final : public Renderer {
private:
    Scene* scene_;                                  // Reference to scene asset
    Film* film_;                                    // Reference to film asset for output
    int num_verts_;                                 // Number of vertices
    std::optional<unsigned int> seed_;              // Random seed
    Component::Ptr<scheduler::Scheduler> sched_;    // Scheduler for parallel processing
    Portal portal_;                                 // Underlying portal

    #if BDPT_PORTAL_PER_STRATEGY_FILM
    mutable std::vector<Ptr<Film>> strategy_films_;
    std::unordered_map<std::string, Film*> strategy_film_name_map_;
    #endif

public:
    virtual Component* underlying(const std::string& name) const override {
        return strategy_film_name_map_.at(name);
    }

    virtual void construct(const Json& prop) override {
        scene_ = json::comp_ref<Scene>(prop, "scene");
        film_ = json::comp_ref<Film>(prop, "output");
        const int min_verts = json::value<int>(prop, "min_verts");
        const int max_verts = json::value<int>(prop, "max_verts");
        if (min_verts != max_verts) {
            LM_THROW_EXCEPTION(Error::InvalidArgument, "min_verts must be equal to max_verts");
        }
        num_verts_ = max_verts;

        seed_ = json::value_or_none<unsigned int>(prop, "seed");
        const auto sched_name = json::value<std::string>(prop, "scheduler");
        sched_ = comp::create<scheduler::Scheduler>(
            "scheduler::spi::" + sched_name, make_loc("scheduler"), prop);

        // ----------------------------------------------------------------------------------------

        // Load portal
        auto ps = prop["portal"];
        if (ps.is_array()) {
            // The portal is specified by array of vec3
            portal_ = Portal(ps[0], ps[1], ps[2]);
        }
        else if (ps.is_string()) {
            // The portal is specified by mesh
            // Extract 4 vertices from the mesh
            auto* portal_mesh = json::comp_ref<Mesh>(prop, "portal");
            if (portal_mesh->num_triangles() != 2) {
                LM_THROW_EXCEPTION(Error::InvalidArgument, "Portal is not a quad");
            }
            const auto tri = portal_mesh->triangle_at(0);

            /*
                   p3
                 / |
              p1 - p2
            */
            portal_ = Portal(tri.p2.p, tri.p3.p, tri.p1.p);
        }
        else {
            LM_THROW_EXCEPTION(Error::InvalidArgument, "Invalid type for portal parameter");
        }

        // ---------------------------------------------------------------------------------------- 

        #if BDPT_PORTAL_PER_STRATEGY_FILM
        const auto size = film_->size();
        for (int s = 0; s <= num_verts_ - 2; s++) {
            const auto name = fmt::format("film_{}", s);
            auto film = comp::create<Film>("film::bitmap", make_loc(name), {
                    {"w", size.w},
                    {"h", size.h}
                });
            film->clear();
            strategy_film_name_map_[name] = film.get();
            strategy_films_.push_back(std::move(film));
        }
        #endif
    }

    virtual Json render() const override {
        scene_->require_renderable();
        film_->clear();
        const auto size = film_->size();
        timer::ScopedTimer st;
        
        // Execute parallel process
        const auto processed = sched_->run([&](long long, long long, int threadid) {
            // Per-thread random number generator
            thread_local Rng rng(seed_ ? *seed_ + threadid : math::rng_seed());

            // Sample subpaths
            const auto subpathE = path::sample_subpath(rng, scene_, num_verts_, TransDir::EL);
            const auto subpathL = path::sample_subpath(rng, scene_, num_verts_, TransDir::LE);
            const int nE = subpathE.num_verts();
            const int nL = subpathL.num_verts();

            // Sample intermediate path
            const auto subpathI = portalbidir::sample_intermediate_subpath(rng, scene_, portal_);
            const int nI = subpathI.num_verts();
            if (nI < 2) {
                // We need a valid intermediate subpath
                return;
            }

            // Generate full paths with number of vertices num_verts
            // s: number of vertices in light subpath
            // t: number of vertices in eye subpath
            // r: number of vertices in intermediate subpath is fixed to 2
            // num_verts = s + t + 2
            const int r = 2;
            for (int s = 0; s <= num_verts_; s++) {
                const int t = num_verts_ - r - s;
                if (t < 0 || nE < t) {
                    continue;
                }
                if (s < 0 || nL < s) {
                    continue;
                }

                // Connect subpaths and generate a full path
                const auto path = portalbidir::connect_subpaths(scene_, subpathL, subpathE, subpathI, s, t);
                if (!path) {
                    // Failed connection
                    continue;
                }

                #if BDPT_PORTAL_POLL_PATHS
                if (threadid == 0) {
                    debug::poll({
                        {"id", "path"},
                        {"path", *path}
                    });
                }
                #endif

                // Evaluate contribution and probability
                const auto f = portalbidir::eval_measurement_contrb(*path, scene_, s);
                if (math::is_zero(f)) {
                    continue;
                }
                const auto p = portalbidir::pdf(*path, scene_, portal_, s);
                if (p == 0_f) {
                    continue;
                }

                // Unweighted contribution
                const auto C_unweighted = f / p;

                // MIS weight
                const auto w = portalbidir::eval_mis_weight(*path, scene_, portal_, s);

                // Weighted contribution
                const auto C = w * C_unweighted;

                // Accumulate contribution
                const auto rp = path->raster_position(scene_);
                film_->splat(rp, C);
                #if BDPT_PORTAL_PER_STRATEGY_FILM
                auto& strategy_film = strategy_films_[s];
                strategy_film->splat(rp, C_unweighted);
                #endif
            }
        });

        // Rescale film
        const auto scale = Float(size.w * size.h) / processed;
        film_->rescale(scale);
        #if BDPT_PORTAL_PER_STRATEGY_FILM
        for (int s = 0; s <= num_verts_ - 2; s++) {
            strategy_films_[s]->rescale(scale);
        }
        #endif

        return {
            {"processed", processed},
            {"elapsed", st.now()}
        };
    }
};

LM_COMP_REG_IMPL(Renderer_Portal_BDPT_Fixed, "renderer::portal_bdpt_fixed");

/*
	Implements portal-based BDPT (simplified version).
	Simplifications:

	  - Number of portals is limited to one.
	  - Only consider the strategies using portals.
	  - Portal edge (path edge passing through a portal) is limited to length 1.
*/
class Renderer_Portal_BDPT_Inter final : public Renderer {
private:
	Scene* scene_;                                  // Reference to scene asset
	Film* film_;                                    // Reference to film asset for output
	int min_verts_;                                 // Minimum number of path vertices
	int max_verts_;                                 // Maximum number of path vertices
	std::optional<unsigned int> seed_;              // Random seed
	Component::Ptr<scheduler::Scheduler> sched_;    // Scheduler for parallel processing
	Portal portal_;                                 // Underlying portal

#if BDPT_PORTAL_PER_STRATEGY_FILM
	mutable std::vector<std::vector<Ptr<Film>>> strategy_films_;
	std::unordered_map<std::string, Film*> strategy_film_name_map_;
#endif

public:
	virtual Component* underlying(const std::string& name) const override {
		return strategy_film_name_map_.at(name);
	}

	virtual void construct(const Json& prop) override {
		scene_ = json::comp_ref<Scene>(prop, "scene");
		film_ = json::comp_ref<Film>(prop, "output");
		min_verts_ = json::value<int>(prop, "min_verts", 2);
		max_verts_ = json::value<int>(prop, "max_verts");

		seed_ = json::value_or_none<unsigned int>(prop, "seed");
		const auto sched_name = json::value<std::string>(prop, "scheduler");
		sched_ = comp::create<scheduler::Scheduler>(
			"scheduler::spi::" + sched_name, make_loc("scheduler"), prop);

		// ----------------------------------------------------------------------------------------

		// Load portal
		auto ps = prop["portal"];
		if (ps.is_array()) {
			// The portal is specified by array of vec3
			portal_ = Portal(ps[0], ps[1], ps[2]);
		}
		else if (ps.is_string()) {
			// The portal is specified by mesh
			// Extract 4 vertices from the mesh
			auto* portal_mesh = json::comp_ref<Mesh>(prop, "portal");
			if (portal_mesh->num_triangles() != 2) {
				LM_THROW_EXCEPTION(Error::InvalidArgument, "Portal is not a quad");
			}
			const auto tri = portal_mesh->triangle_at(0);

			/*
				   p3
				 / |
			  p1 - p2
			*/
			portal_ = Portal(tri.p2.p, tri.p3.p, tri.p1.p);
		}
		else {
			LM_THROW_EXCEPTION(Error::InvalidArgument, "Invalid type for portal parameter");
		}

		// ---------------------------------------------------------------------------------------- 

#if BDPT_PORTAL_PER_STRATEGY_FILM
		const auto size = film_->size();
		for (int k = 2; k <= max_verts_; k++) {
			strategy_films_.emplace_back();
			for (int s = 0; s <= k - 2; s++) {				// Subtract intermediate path length
				const auto name = fmt::format("film_{}_{}", k, s);
				auto film = comp::create<Film>("film::bitmap", make_loc(name), {
					{"w", size.w},
					{"h", size.h}
					});
				film->clear();
				strategy_film_name_map_[name] = film.get();
				strategy_films_.back().push_back(std::move(film));
			}
		}
#endif
	}

	virtual Json render() const override {
		scene_->require_renderable();
		film_->clear();
		const auto size = film_->size();
		timer::ScopedTimer st;

		// Execute parallel process
		const auto processed = sched_->run([&](long long, long long, int threadid) {
			// Per-thread random number generator
			thread_local Rng rng(seed_ ? *seed_ + threadid : math::rng_seed());

			// Sample subpaths
			const auto subpathE = path::sample_subpath(rng, scene_, max_verts_, TransDir::EL);
			const auto subpathL = path::sample_subpath(rng, scene_, max_verts_, TransDir::LE);
			const int nE = subpathE.num_verts();
			const int nL = subpathL.num_verts();

			// Sample intermediate path
			const auto subpathI = portalbidir::sample_intermediate_subpath(rng, scene_, portal_);
			const int nI = subpathI.num_verts();
			if (nI < 2) {
				// We need a valid intermediate subpath
				return;
			}

			// Generate full paths with number of vertices num_verts
			// s: number of vertices in light subpath
			// t: number of vertices in eye subpath
			// r: number of vertices in intermediate subpath is fixed to 2
			// num_verts = s + t + 2
			const int r = 2;
			for (int s = 0; s <= nL; s++) {
				for (int t = 0; t <= nE; t++) {

					const int k = s + t + r;
					if (k < min_verts_ || max_verts_ < k) {
						continue;
					}
					// Connect subpaths and generate a full path
					const auto path = portalbidir::connect_subpaths_inter(scene_, subpathL, subpathE, subpathI, s, t);
					if (!path) {
						// Failed connection
						continue;
					}

#if BDPT_PORTAL_POLL_PATHS
					if (threadid == 0) {
						debug::poll({
							{"id", "path"},
							{"path", *path}
							});
					}
#endif

					// Evaluate contribution and probability
					const auto f = portalbidir::eval_measurement_contrb_inter(*path, scene_, s);
					if (math::is_zero(f)) {
						continue;
					}
					const auto p = portalbidir::pdf(*path, scene_, portal_, s);
					if (p == 0_f) {
						continue;
					}

					// Unweighted contribution
					const auto C_unweighted = f / p;

					// MIS weight
					const auto w = portalbidir::eval_mis_weight(*path, scene_, portal_, s);

					// Weighted contribution
					const auto C = w * C_unweighted;

					// Accumulate contribution
					const auto rp = path->raster_position(scene_);
					film_->splat(rp, C);
#if BDPT_PORTAL_PER_STRATEGY_FILM
					auto& strategy_film = strategy_films_[k - 2][s];
					strategy_film->splat(rp, C_unweighted);
#endif
				}
			}
			});

		// Rescale film
		const auto scale = Float(size.w * size.h) / processed;
		film_->rescale(scale);
#if BDPT_PORTAL_PER_STRATEGY_FILM
		for (int k = 2; k <= max_verts_; k++) {
			for (int s = 0; s <= k - 2; s++) {				// Subtract intermediate length
				strategy_films_[k - 2][s]->rescale(scale);
			}
		}
#endif

		return {
			{"processed", processed},
			{"elapsed", st.now()}
		};
	}
};

LM_COMP_REG_IMPL(Renderer_Portal_BDPT_Inter, "renderer::portal_bdpt_inter");


// For next stage: subpathI.length() > 1
// - Modify intermediate subpath sampling
//  -> Call sample_subpath_from_endpoint(Rng& rng, Path& path, const Scene* scene, int max_verts, TransDir trans_dir)
//     with path already initialized with primary position
// 


class Renderer_Portal_BDPT_Fixed_Test final : public Renderer {
private:
	Scene* scene_;                                  // Reference to scene asset
	Film* film_;                                    // Reference to film asset for output
	int num_verts_;                                 // Number of vertices
	std::optional<unsigned int> seed_;              // Random seed
	Component::Ptr<scheduler::Scheduler> sched_;    // Scheduler for parallel processing
	Portal portal_;                                 // Underlying portal

#if BDPT_PORTAL_PER_STRATEGY_FILM
	mutable std::vector<Ptr<Film>> strategy_films_;
	std::unordered_map<std::string, Film*> strategy_film_name_map_;
#endif

public:
	virtual Component* underlying(const std::string& name) const override {
		return strategy_film_name_map_.at(name);
	}

	virtual void construct(const Json& prop) override {
		scene_ = json::comp_ref<Scene>(prop, "scene");
		film_ = json::comp_ref<Film>(prop, "output");
		const int min_verts = json::value<int>(prop, "min_verts");
		const int max_verts = json::value<int>(prop, "max_verts");
		if (min_verts != max_verts) {
			LM_THROW_EXCEPTION(Error::InvalidArgument, "min_verts must be equal to max_verts");
		}
		num_verts_ = max_verts;

		seed_ = json::value_or_none<unsigned int>(prop, "seed");
		const auto sched_name = json::value<std::string>(prop, "scheduler");
		sched_ = comp::create<scheduler::Scheduler>(
			"scheduler::spi::" + sched_name, make_loc("scheduler"), prop);

		// ----------------------------------------------------------------------------------------

		// Load portal
		auto ps = prop["portal"];
		if (ps.is_array()) {
			// The portal is specified by array of vec3
			portal_ = Portal(ps[0], ps[1], ps[2]);
		}
		else if (ps.is_string()) {
			// The portal is specified by mesh
			// Extract 4 vertices from the mesh
			auto* portal_mesh = json::comp_ref<Mesh>(prop, "portal");
			if (portal_mesh->num_triangles() != 2) {
				LM_THROW_EXCEPTION(Error::InvalidArgument, "Portal is not a quad");
			}
			const auto tri = portal_mesh->triangle_at(0);

			/*
				   p3
				 / |
			  p1 - p2
			*/
			portal_ = Portal(tri.p2.p, tri.p3.p, tri.p1.p);
		}
		else {
			LM_THROW_EXCEPTION(Error::InvalidArgument, "Invalid type for portal parameter");
		}

		// ---------------------------------------------------------------------------------------- 

#if BDPT_PORTAL_PER_STRATEGY_FILM
		const auto size = film_->size();
		for (int s = 0; s <= num_verts_ - 2; s++) {
			const auto name = fmt::format("film_{}", s);
			auto film = comp::create<Film>("film::bitmap", make_loc(name), {
					{"w", size.w},
					{"h", size.h}
				});
			film->clear();
			strategy_film_name_map_[name] = film.get();
			strategy_films_.push_back(std::move(film));
		}
#endif
	}

	virtual Json render() const override {
		scene_->require_renderable();
		film_->clear();
		const auto size = film_->size();
		timer::ScopedTimer st;

		// Execute parallel process
		const auto processed = sched_->run([&](long long, long long, int threadid) {
			// Per-thread random number generator
			thread_local Rng rng(seed_ ? *seed_ + threadid : math::rng_seed());

			// Sample subpaths
			const auto subpathE = path::sample_subpath(rng, scene_, num_verts_, TransDir::EL);
			const auto subpathL = path::sample_subpath(rng, scene_, num_verts_, TransDir::LE);
			const int nE = subpathE.num_verts();
			const int nL = subpathL.num_verts();

			// Sample intermediate path
			const auto subpathI = portalbidir::sample_intermediate_subpath(rng, scene_, portal_);
			const int nI = subpathI.num_verts();
			if (nI < 2) {
				// We need a valid intermediate subpath
				return;
			}

			// Generate full paths with number of vertices num_verts
			// s: number of vertices in light subpath
			// t: number of vertices in eye subpath
			// r: number of vertices in intermediate subpath is fixed to 2
			// num_verts = s + t + 2
			const int r = 2;
			for (int s = 0; s <= num_verts_; s++) {
				const int t = num_verts_ - r - s;
				if (t < 0 || nE < t) {
					continue;
				}
				if (s < 0 || nL < s) {
					continue;
				}

				// Connect subpaths and generate a full path
				const auto path = portalbidir::connect_subpaths(scene_, subpathL, subpathE, subpathI, s, t);
				if (!path) {
					// Failed connection
					continue;
				}

#if BDPT_PORTAL_POLL_PATHS
				if (threadid == 0) {

					const auto* vE2 = path->vertex_at(1, TransDir::EL);

					// Poll paths where the raster position is on the back wall
					if (vE2 != nullptr && abs(vE2->sp.geom.p.z - (-1.05467)) < 0.01)
					{
						for (int iLen = 2; iLen < path->num_verts(); iLen++)
						{
							const auto* v_Current = path->vertex_at(iLen, TransDir::EL);

							// ...and the path leaves the light room again at some point
							if (v_Current->sp.geom.p.z > 1.09403 + 0.01)
							{
								debug::poll({
									{"id", "path"},
									{"path", *path}
									});
							}
						}
					}
				}
#endif

				// Evaluate contribution and probability
				const auto f = portalbidir::eval_measurement_contrb(*path, scene_, s);
				if (math::is_zero(f)) {
					continue;
				}
				const auto p = portalbidir::pdf(*path, scene_, portal_, s);
				if (p == 0_f) {
					continue;
				}

				// Unweighted contribution
				const auto C_unweighted = f / p;

				// MIS weight
				const auto w = portalbidir::eval_mis_weight(*path, scene_, portal_, s);

				// Weighted contribution
				const auto C = w * C_unweighted;

				// Accumulate contribution
				const auto rp = path->raster_position(scene_);
				film_->splat(rp, C);
#if BDPT_PORTAL_PER_STRATEGY_FILM
				auto& strategy_film = strategy_films_[s];
				strategy_film->splat(rp, C_unweighted);
#endif
			}
			});

		// Rescale film
		const auto scale = Float(size.w * size.h) / processed;
		film_->rescale(scale);
#if BDPT_PORTAL_PER_STRATEGY_FILM
		for (int s = 0; s <= num_verts_ - 2; s++) {
			strategy_films_[s]->rescale(scale);
		}
#endif

		return {
			{"processed", processed},
			{"elapsed", st.now()}
		};
	}
};

LM_COMP_REG_IMPL(Renderer_Portal_BDPT_Fixed_Test, "renderer::portal_bdpt_fixed_test");

LM_NAMESPACE_END(LM_NAMESPACE)
