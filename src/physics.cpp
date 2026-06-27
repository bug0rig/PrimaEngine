#include <nanobind/nanobind.h>
#include <nanobind/operators.h>
#include <nanobind/ndarray.h>
#include <nanobind/stl/string.h>
#include <nanobind/stl/vector.h>
#include <nanobind/stl/optional.h>
#include <cmath>
#include <cstring>
#include <cfloat>
#include <vector>
#include <algorithm>

namespace nb = nanobind;
using namespace nb::literals;

constexpr float EPS = 1e-6f;

// =========================================================================
// Vec3
// =========================================================================

struct Vec3 {
    float x, y, z;
    Vec3() : x(0), y(0), z(0) {}
    Vec3(float x, float y, float z) : x(x), y(y), z(z) {}

    Vec3 operator+(const Vec3& o) const { return {x + o.x, y + o.y, z + o.z}; }
    Vec3 operator-(const Vec3& o) const { return {x - o.x, y - o.y, z - o.z}; }
    Vec3 operator*(float s) const { return {x * s, y * s, z * s}; }
    Vec3 operator/(float s) const { return {x / s, y / s, z / s}; }
    Vec3 operator-() const { return {-x, -y, -z}; }

    float length() const { return std::sqrt(x*x + y*y + z*z); }
    float length_sq() const { return x*x + y*y + z*z; }

    Vec3 normalized() const {
        float l = length();
        if (l < EPS) return {0, 0, 0};
        return {x / l, y / l, z / l};
    }

    float dot(const Vec3& o) const { return x * o.x + y * o.y + z * o.z; }
    Vec3 cross(const Vec3& o) const {
        return { y * o.z - z * o.y, z * o.x - x * o.z, x * o.y - y * o.x };
    }

    nb::list to_list() const {
        nb::list l; l.append(nb::float_(x)); l.append(nb::float_(y)); l.append(nb::float_(z));
        return l;
    }

    nb::list to_array() const {
        nb::list l; l.append(nb::float_(x)); l.append(nb::float_(y)); l.append(nb::float_(z));
        return l;
    }

    std::string repr() const {
        char buf[64]; std::snprintf(buf, sizeof(buf), "(%.3f, %.3f, %.3f)", x, y, z); return buf;
    }

    static Vec3 zero() { return {0, 0, 0}; }
    static Vec3 up() { return {0, 1, 0}; }
    static Vec3 right() { return {1, 0, 0}; }
    static Vec3 forward() { return {0, 0, -1}; }
    static Vec3 lerp(const Vec3& a, const Vec3& b, float t) { return a + (b - a) * t; }
};

// =========================================================================
// Mat3x3 - must be before RigidBody
// =========================================================================

struct Mat3x3 {
    float m[9];

    Mat3x3() { std::memset(m, 0, sizeof(m)); m[0] = m[4] = m[8] = 1.0f; }

    Mat3x3 operator*(const Mat3x3& o) const {
        Mat3x3 r;
        for (int i = 0; i < 3; i++)
            for (int j = 0; j < 3; j++) {
                float sum = 0;
                for (int k = 0; k < 3; k++) sum += m[i*3+k] * o.m[k*3+j];
                r.m[i*3+j] = sum;
            }
        return r;
    }

    Vec3 operator*(const Vec3& v) const {
        return {
            m[0]*v.x + m[1]*v.y + m[2]*v.z,
            m[3]*v.x + m[4]*v.y + m[5]*v.z,
            m[6]*v.x + m[7]*v.y + m[8]*v.z
        };
    }

    Mat3x3 transpose() const {
        Mat3x3 r;
        for (int i = 0; i < 3; i++)
            for (int j = 0; j < 3; j++)
                r.m[i*3+j] = m[j*3+i];
        return r;
    }

    static Mat3x3 zero() { Mat3x3 r; std::memset(r.m, 0, sizeof(r.m)); return r; }

    static Mat3x3 diagonal(float d) {
        Mat3x3 r; std::memset(r.m, 0, sizeof(r.m));
        r.m[0] = r.m[4] = r.m[8] = d;
        return r;
    }
};

// =========================================================================
// Quaternion
// =========================================================================

struct Quat {
    float w, x, y, z;
    Quat() : w(1), x(0), y(0), z(0) {}
    Quat(float w, float x, float y, float z) : w(w), x(x), y(y), z(z) {}

    static Quat identity() { return {1, 0, 0, 0}; }

    static Quat from_axis_angle(const Vec3& axis, float angle) {
        float half = angle * 0.5f;
        float s = std::sin(half);
        Vec3 n = axis.normalized();
        return {std::cos(half), n.x * s, n.y * s, n.z * s};
    }

    // Ry(yaw) * Rx(pitch) * Rz(roll) – matches scene: t * ry * rx * rz * s
    static Quat from_euler(float pitch, float yaw, float roll) {
        float cp = std::cos(pitch*0.5f), sp = std::sin(pitch*0.5f);
        float cy = std::cos(yaw*0.5f),   sy = std::sin(yaw*0.5f);
        float cr = std::cos(roll*0.5f),  sr = std::sin(roll*0.5f);
        return {
            cy*cp*cr + sy*sp*sr,   // w
            cy*sp*cr + sy*cp*sr,   // x
            sy*cp*cr - cy*sp*sr,   // y
            cy*cp*sr - sy*sp*cr    // z
        };
    }

    // Extract Ry*Rx*Rz Euler angles (pitch, yaw, roll) from this quaternion
    Vec3 to_euler() const {
        float sp = 2.0f * (w*x - y*z);
        if (sp > 1.0f) sp = 1.0f;
        if (sp < -1.0f) sp = -1.0f;
        float pitch = std::asin(sp);
        float yaw   = std::atan2(2.0f * (x*z + w*y), 1.0f - 2.0f*(x*x + y*y));
        float roll  = std::atan2(2.0f * (w*z + x*y), 1.0f - 2.0f*(x*x + z*z));
        return {pitch, yaw, roll};
    }

    Quat conjugate() const {
        return {w, -x, -y, -z};
    }

    Vec3 rotate(const Vec3& v) const {
        float tx = 2*(y*v.z - z*v.y), ty = 2*(z*v.x - x*v.z), tz = 2*(x*v.y - y*v.x);
        return {
            v.x + w*tx + (y*tz - z*ty),
            v.y + w*ty + (z*tx - x*tz),
            v.z + w*tz + (x*ty - y*tx)
        };
    }

    Quat operator*(const Quat& o) const {
        return {
            w*o.w - x*o.x - y*o.y - z*o.z,
            w*o.x + x*o.w + y*o.z - z*o.y,
            w*o.y - x*o.z + y*o.w + z*o.x,
            w*o.z + x*o.y - y*o.x + z*o.w
        };
    }

    Quat normalized() const {
        float l = std::sqrt(w*w + x*x + y*y + z*z);
        if (l < EPS) return {1, 0, 0, 0};
        return {w/l, x/l, y/l, z/l};
    }

    nb::list to_list() const {
        nb::list l; l.append(nb::float_(w)); l.append(nb::float_(x));
        l.append(nb::float_(y)); l.append(nb::float_(z));
        return l;
    }

    nb::list to_array() const {
        nb::list l; l.append(nb::float_(w)); l.append(nb::float_(x));
        l.append(nb::float_(y)); l.append(nb::float_(z));
        return l;
    }

    std::string repr() const {
        char buf[80]; std::snprintf(buf, sizeof(buf), "(%.3f, %.3f, %.3f, %.3f)", w, x, y, z); return buf;
    }
};

// Build rotation matrix from quaternion
Mat3x3 quat_to_mat3(const Quat& q) {
    float w = q.w, x = q.x, y = q.y, z = q.z;
    Mat3x3 r;
    r.m[0] = 1 - 2*(y*y + z*z); r.m[1] = 2*(x*y - w*z);     r.m[2] = 2*(x*z + w*y);
    r.m[3] = 2*(x*y + w*z);     r.m[4] = 1 - 2*(x*x + z*z); r.m[5] = 2*(y*z - w*x);
    r.m[6] = 2*(x*z - w*y);     r.m[7] = 2*(y*z + w*x);     r.m[8] = 1 - 2*(x*x + y*y);
    return r;
}

// =========================================================================
// Collision shape
// =========================================================================

enum class ShapeType { SPHERE, BOX, PLANE, CAPSULE, MESH };

struct CollisionShape {
    ShapeType type{ShapeType::SPHERE};
    float params[4]{0, 0, 0, 0};
    std::vector<float> mesh_verts;
    std::vector<int> mesh_indices;

    static CollisionShape make_sphere(float radius) {
        CollisionShape s; s.type = ShapeType::SPHERE; s.params[0] = radius; return s;
    }
    static CollisionShape make_box(float hx, float hy, float hz) {
        CollisionShape s; s.type = ShapeType::BOX; s.params[0] = hx; s.params[1] = hy; s.params[2] = hz; return s;
    }
    static CollisionShape make_plane(const Vec3& normal, float offset) {
        CollisionShape s; s.type = ShapeType::PLANE;
        s.params[0] = normal.x; s.params[1] = normal.y; s.params[2] = normal.z; s.params[3] = offset;
        return s;
    }
    static CollisionShape make_capsule(float radius, float half_height) {
        CollisionShape s; s.type = ShapeType::CAPSULE; s.params[0] = radius; s.params[1] = half_height; return s;
    }
    static CollisionShape make_mesh(const std::vector<float>& verts, const std::vector<int>& indices) {
        CollisionShape s; s.type = ShapeType::MESH; s.mesh_verts = verts; s.mesh_indices = indices; return s;
    }
};

// =========================================================================
// Contact
// =========================================================================

struct Contact {
    Vec3 point, normal;
    float penetration{0};
    float accumulated_jn{0};
    int body_a{-1}, body_b{-1};
};

// =========================================================================
// Raycast hit
// =========================================================================

struct RaycastHit {
    bool hit{false};
    Vec3 point, normal;
    float distance{0};
    int body_id{-1};
};

// =========================================================================
// RigidBody
// =========================================================================

struct RigidBody {
    Vec3 position;
    Quat rotation;
    Vec3 linear_velocity, angular_velocity;
    float mass{1}, inv_mass{1};
    float restitution{0.3f}, friction{0.5f};
    bool is_static{false};
    CollisionShape shape;
    int id{-1};
    Mat3x3 inv_inertia;

    void set_mass(float m) {
        mass = m;
        inv_mass = (m > EPS && !is_static) ? 1.0f / m : 0.0f;
    }

    void set_static(bool s) {
        is_static = s;
        if (s) { inv_mass = 0; inv_inertia = Mat3x3::zero(); }
    }
};

// =========================================================================
// Collision detection
// =========================================================================

Vec3 support_point(const RigidBody& body, const Vec3& dir) {
    Vec3 local_dir = body.rotation.conjugate().rotate(dir);
    const auto& s = body.shape;
    Vec3 local_support;

    switch (s.type) {
    case ShapeType::SPHERE: {
        float r = s.params[0];
        local_support = local_dir.normalized() * r;
        break;
    }
    case ShapeType::BOX: {
        float hx = s.params[0], hy = s.params[1], hz = s.params[2];
        Vec3 d = local_dir.normalized();
        local_support = {std::copysignf(hx, d.x), std::copysignf(hy, d.y), std::copysignf(hz, d.z)};
        break;
    }
    case ShapeType::CAPSULE: {
        float r = s.params[0], hh = s.params[1];
        Vec3 d = local_dir.normalized();
        Vec3 seg_dir{0, 1, 0};
        Vec3 seg_support = seg_dir * (d.y >= 0 ? hh : -hh);
        local_support = seg_support + d * r;
        break;
    }
    case ShapeType::MESH: {
        float best_dot = -FLT_MAX;
        int n = (int)s.mesh_verts.size() / 3;
        for (int i = 0; i < n; i++) {
            Vec3 v(s.mesh_verts[i*3], s.mesh_verts[i*3+1], s.mesh_verts[i*3+2]);
            float d = v.dot(local_dir);
            if (d > best_dot) { best_dot = d; local_support = v; }
        }
        break;
    }
    case ShapeType::PLANE:
        local_support = local_dir * -1000.0f;
        break;
    }

    return body.position + body.rotation.rotate(local_support);
}

bool collide_sphere_sphere(const RigidBody& a, const RigidBody& b, Contact& c) {
    float ra = a.shape.params[0], rb = b.shape.params[0];
    Vec3 diff = b.position - a.position;
    float dist_sq = diff.length_sq();
    float sum_r = ra + rb;
    if (dist_sq >= sum_r * sum_r) return false;
    float dist = std::sqrt(dist_sq);
    if (dist < EPS) {
        c.point = a.position; c.normal = {0, 1, 0}; c.penetration = sum_r;
        return true;
    }
    // n points from b toward a (convention: body_b → body_a)
    Vec3 n = (a.position - b.position) / dist;
    // Contact = midpoint between surfaces along collision line
    c.point = (a.position + b.position) * 0.5f + n * (rb - ra) * 0.5f;
    c.normal = n;
    c.penetration = sum_r - dist;
    return true;
}

bool collide_sphere_plane(const RigidBody& sphere, const RigidBody& plane, Contact& c) {
    float r = sphere.shape.params[0];
    Vec3 pn(plane.shape.params[0], plane.shape.params[1], plane.shape.params[2]);
    float po = plane.shape.params[3];
    float dist = sphere.position.dot(pn) - po;
    float pen = -(dist - r);
    if (pen <= 0) return false;
    c.point = sphere.position - pn * (dist + pen * 0.5f);
    c.normal = (dist < 0) ? pn * -1.0f : pn;
    c.penetration = pen;
    return true;
}

bool collide_box_plane(const RigidBody& box, const RigidBody& plane, Contact& c) {
    float hx = box.shape.params[0], hy = box.shape.params[1], hz = box.shape.params[2];
    Vec3 pn(plane.shape.params[0], plane.shape.params[1], plane.shape.params[2]);
    float po = plane.shape.params[3];

    // Get box corners in world space, find deepest penetration
    float max_pen = -FLT_MAX;
    Vec3 deepest_corner;
    for (int i = 0; i < 8; i++) {
        float lx = (i & 1) ? hx : -hx;
        float ly = (i & 2) ? hy : -hy;
        float lz = (i & 4) ? hz : -hz;
        Vec3 corner = box.position + box.rotation.rotate({lx, ly, lz});
        float d = corner.dot(pn) - po;
        float pen = -d;
        if (pen > max_pen) {
            max_pen = pen;
            deepest_corner = corner;
        }
    }

    if (max_pen <= 0) return false;

    c.point = deepest_corner - pn * (max_pen * 0.5f);
    c.normal = pn;
    c.penetration = max_pen;
    return true;
}

bool collide_capsule_plane(const RigidBody& capsule, const RigidBody& plane, Contact& c) {
    float r = capsule.shape.params[0], hh = capsule.shape.params[1];
    Vec3 pn(plane.shape.params[0], plane.shape.params[1], plane.shape.params[2]);
    float po = plane.shape.params[3];

    // Capsule endpoints
    Vec3 end_a = capsule.position + capsule.rotation.rotate({0, -hh, 0});
    Vec3 end_b = capsule.position + capsule.rotation.rotate({0, hh, 0});

    // Check distance from each endpoint + sphere
    float best_pen = -FLT_MAX;
    Vec3 best_point;
    for (int i = 0; i < 2; i++) {
        Vec3 end = (i == 0) ? end_a : end_b;
        float d = end.dot(pn) - po;
        float pen = -(d - r);
        if (pen > best_pen) {
            best_pen = pen;
            best_point = end - pn * (d + pen * 0.5f);
        }
    }

    // Also check closest point on segment to plane
    Vec3 seg = end_b - end_a;
    float seg_len = seg.length();
    if (seg_len > EPS) {
        Vec3 seg_dir = seg / seg_len;
        float t = -pn.dot(end_a - pn * po) / pn.dot(seg_dir);
        // Only check if segment is not parallel to plane
        if (std::abs(pn.dot(seg_dir)) > EPS) {
            t = std::max(0.0f, std::min(seg_len, t)) / seg_len;
            Vec3 closest = end_a + seg * t;
            float d = closest.dot(pn) - po;
            float pen = -(d - r);
            if (pen > best_pen) {
                best_pen = pen;
                best_point = closest - pn * (d + pen * 0.5f);
            }
        }
    }

    if (best_pen <= 0) return false;
    c.point = best_point;
    c.normal = pn;
    c.penetration = best_pen;
    return true;
}

// =========================================================================
// PhysicsWorld
// =========================================================================

struct PhysicsWorld {
    std::vector<RigidBody> bodies;
    std::vector<Contact> contacts;
    Vec3 gravity{0, -9.81f, 0};
    int next_id{0};
    int solver_iterations{8};
    float linear_damping{0.01f};
    float angular_damping{0.01f};
    float cell_size{4.0f};

    int add_body(const RigidBody& body) {
        bodies.push_back(body);
        bodies.back().id = next_id++;
        compute_inertia(bodies.back());
        return bodies.back().id;
    }

    void remove_body(int id) {
        auto it = std::remove_if(bodies.begin(), bodies.end(),
            [id](const RigidBody& b) { return b.id == id; });
        bodies.erase(it, bodies.end());
    }

    RigidBody* get_body(int id) {
        for (auto& b : bodies) if (b.id == id) return &b;
        return nullptr;
    }

    void compute_inertia(RigidBody& body) {
        if (body.is_static || body.inv_mass < EPS) {
            body.inv_inertia = Mat3x3::zero();
            return;
        }
        float m = body.mass;
        const auto& s = body.shape;
        float ix = 1, iy = 1, iz = 1;

        switch (s.type) {
        case ShapeType::SPHERE: {
            float r = s.params[0];
            float i = 0.4f * m * r * r; ix = iy = iz = i; break;
        }
        case ShapeType::BOX: {
            float hx = s.params[0], hy = s.params[1], hz = s.params[2];
            ix = (1.0f/12.0f) * m * (hy*hy + hz*hz);
            iy = (1.0f/12.0f) * m * (hx*hx + hz*hz);
            iz = (1.0f/12.0f) * m * (hx*hx + hy*hy);
            break;
        }
        case ShapeType::CAPSULE: {
            float r = s.params[0], hh = s.params[1];
            float cyl_mass = m * (hh * 2) / (hh * 2 + 4 * r / 3);
            float sph_mass = m - cyl_mass;
            float ic_y = cyl_mass * r * r * 0.5f;
            float ic_x = cyl_mass * (r * r * 0.25f + hh * hh / 3.0f);
            float is = 0.4f * sph_mass * r * r;
            ix = ic_x + is + sph_mass * (hh + r) * (hh + r);
            iy = ic_y + is;
            iz = ix;
            break;
        }
        default: break;
        }

        float inv_ix = (ix > EPS) ? 1.0f/ix : 0;
        float inv_iy = (iy > EPS) ? 1.0f/iy : 0;
        float inv_iz = (iz > EPS) ? 1.0f/iz : 0;
        Mat3x3 inv_local = Mat3x3::diagonal(inv_ix); // will set all diags
        inv_local.m[0] = inv_ix; inv_local.m[4] = inv_iy; inv_local.m[8] = inv_iz;
        Mat3x3 rot = quat_to_mat3(body.rotation);
        body.inv_inertia = rot * inv_local * rot.transpose();
    }

    void update_inertia(RigidBody& body) {
        if (body.is_static || body.inv_mass < EPS) return;
        Mat3x3 rot = quat_to_mat3(body.rotation);
        float m = body.mass;
        const auto& s = body.shape;
        float ix = 1, iy = 1, iz = 1;

        switch (s.type) {
        case ShapeType::SPHERE: {
            float r = s.params[0]; float i = 0.4f * m * r * r; ix = iy = iz = i; break;
        }
        case ShapeType::BOX: {
            float hx = s.params[0], hy = s.params[1], hz = s.params[2];
            ix = (1.0f/12.0f) * m * (hy*hy + hz*hz);
            iy = (1.0f/12.0f) * m * (hx*hx + hz*hz);
            iz = (1.0f/12.0f) * m * (hx*hx + hy*hy);
            break;
        }
        default: break;
        }

        float inv_ix = (ix > EPS) ? 1.0f/ix : 0;
        float inv_iy = (iy > EPS) ? 1.0f/iy : 0;
        float inv_iz = (iz > EPS) ? 1.0f/iz : 0;
        Mat3x3 inv_local;
        inv_local.m[0] = inv_ix; inv_local.m[4] = inv_iy; inv_local.m[8] = inv_iz;
        body.inv_inertia = rot * inv_local * rot.transpose();
    }

    // GJK
    Vec3 support_diff(const RigidBody& a, const RigidBody& b, const Vec3& d) {
        return support_point(a, d) - support_point(b, -d);
    }

    // Compute contact from overlapping GJK simplex.
    // Convention: return normal pointing FROM body_b TOWARD body_a.
    void gjk_contact(const RigidBody& a, const RigidBody& b,
                     Vec3 simplex[], int ssize, Contact& c) {
        // Normal pointing FROM body_b TOWARD body_a.
        c.normal = (a.position - b.position).normalized();
        if (c.normal.length_sq() < 0.5f) c.normal = {0, 1, 0};

        // Project support points onto the contact normal to strip perpendicular
        // components (they would add bogus lever arms to the contact point).
        Vec3 local_a_raw = support_point(a, -c.normal);
        Vec3 local_b_raw = support_point(b, c.normal);
        float da = (local_a_raw - a.position).dot(c.normal);
        float db = (local_b_raw - b.position).dot(c.normal);
        Vec3 local_a = a.position + c.normal * da;
        Vec3 local_b = b.position + c.normal * db;

        c.point = (local_a + local_b) * 0.5f;
        c.penetration = (local_b - local_a).dot(c.normal);
        if (c.penetration < 0) c.penetration = -c.penetration;
    }

    bool gjk_collide(const RigidBody& a, const RigidBody& b, Contact& c) {
        Vec3 dir = (b.position - a.position).normalized();
        if (dir.length_sq() < EPS) dir = {0, 1, 0};

        Vec3 simplex[4];
        int ssize = 0;

        simplex[0] = support_diff(a, b, dir);
        ssize = 1;
        dir = -simplex[0];

        for (int iter = 0; iter < 64; iter++) {
            Vec3 p = support_diff(a, b, dir);
            if (p.dot(dir) < 0) return false;
            simplex[ssize++] = p;

            if (ssize == 2) {
                Vec3 a0 = simplex[1], b0 = simplex[0];
                Vec3 ab = b0 - a0, ao = -a0;
                dir = ab.cross(ao).cross(ab);
                if (dir.length_sq() < EPS) {
                    dir = ab.cross({1, 0, 0}); if (dir.length_sq() < EPS) dir = ab.cross({0, 0, 1});
                }
                dir = dir.normalized();
            } else if (ssize == 3) {
                Vec3 a0 = simplex[2], b0 = simplex[1], c0 = simplex[0];
                Vec3 ab = b0 - a0, ac = c0 - a0;
                Vec3 abc = ab.cross(ac);
                Vec3 ao = -a0;

                if (abc.cross(ac).dot(ao) > 0) {
                    simplex[0] = a0; simplex[1] = c0; ssize = 2;
                    dir = ac.cross(ao).cross(ac);
                } else if (ab.cross(abc).dot(ao) > 0) {
                    simplex[0] = a0; simplex[1] = b0; ssize = 2;
                    dir = ab.cross(ao).cross(ab);
                } else {
                    // Overlap found (origin in/behind triangle)
                    gjk_contact(a, b, simplex, 3, c);
                    return true;
                }
            } else if (ssize == 4) {
                gjk_contact(a, b, simplex, 4, c);
                return true;
            }

            if (dir.length_sq() < EPS) dir = {1, 0, 0};
            else dir = dir.normalized();
        }
        return false;
    }

    std::vector<Contact> detect_collisions() {
        std::vector<Contact> all_contacts;
        int n = (int)bodies.size();

        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                auto& a = bodies[i];
                auto& b = bodies[j];
                if (a.is_static && b.is_static) continue;

                Contact c;
                c.body_a = a.id; c.body_b = b.id;
                bool found = false;

                auto ta = a.shape.type, tb = b.shape.type;

                if (ta == ShapeType::SPHERE && tb == ShapeType::SPHERE) {
                    found = collide_sphere_sphere(a, b, c);
                } else if ((ta == ShapeType::SPHERE && tb == ShapeType::PLANE) || (ta == ShapeType::PLANE && tb == ShapeType::SPHERE)) {
                    if (ta == ShapeType::SPHERE) found = collide_sphere_plane(a, b, c);
                    else { found = collide_sphere_plane(b, a, c); std::swap(c.body_a, c.body_b); }
                } else if ((ta == ShapeType::BOX && tb == ShapeType::PLANE) || (ta == ShapeType::PLANE && tb == ShapeType::BOX)) {
                    if (ta == ShapeType::BOX) found = collide_box_plane(a, b, c);
                    else { found = collide_box_plane(b, a, c); std::swap(c.body_a, c.body_b); }
                } else if ((ta == ShapeType::CAPSULE && tb == ShapeType::PLANE) || (ta == ShapeType::PLANE && tb == ShapeType::CAPSULE)) {
                    if (ta == ShapeType::CAPSULE) found = collide_capsule_plane(a, b, c);
                    else { found = collide_capsule_plane(b, a, c); std::swap(c.body_a, c.body_b); }
                } else if (ta == ShapeType::PLANE || tb == ShapeType::PLANE) {
                    continue; // plane vs other unhandled shape
                } else {
                    found = gjk_collide(a, b, c);
                }

                if (found) all_contacts.push_back(c);
            }
        }
        return all_contacts;
    }

    void resolve_contacts() {
        for (int iter = 0; iter < solver_iterations; iter++) {
            for (auto& c : contacts) {
                auto* body_a = get_body(c.body_a);
                auto* body_b = get_body(c.body_b);
                if (!body_a || !body_b) continue;

                Vec3 n = c.normal;
                Vec3 r1 = c.point - body_a->position;
                Vec3 r2 = c.point - body_b->position;

                Vec3 v1 = body_a->linear_velocity + body_a->angular_velocity.cross(r1);
                Vec3 v2 = body_b->linear_velocity + body_b->angular_velocity.cross(r2);
                Vec3 dv = v1 - v2;
                float vn = dv.dot(n);

                float e = std::min(body_a->restitution, body_b->restitution);
                float numerator = -(1 + e) * vn;
                Vec3 r1xn = r1.cross(n), r2xn = r2.cross(n);
                float inv_mass_sum = body_a->inv_mass + body_b->inv_mass;
                float ang = r1xn.dot(body_a->inv_inertia * r1xn) + r2xn.dot(body_b->inv_inertia * r2xn);
                float denom = inv_mass_sum + ang;
                if (denom < EPS) continue;

                float jn = numerator / denom;
                Vec3 impulse = n * jn;
                body_a->linear_velocity = body_a->linear_velocity + impulse * body_a->inv_mass;
                body_b->linear_velocity = body_b->linear_velocity - impulse * body_b->inv_mass;

                Vec3 i1_r1xn = body_a->inv_inertia * r1xn;
                Vec3 i2_r2xn = body_b->inv_inertia * r2xn;
                body_a->angular_velocity = body_a->angular_velocity + i1_r1xn * jn;
                body_b->angular_velocity = body_b->angular_velocity - i2_r2xn * jn;

                // Friction
                Vec3 tangent = dv - n * vn;
                float vt = tangent.length();
                if (vt > EPS) {
                    tangent = tangent / vt;
                    float friction = std::sqrt(body_a->friction * body_b->friction);
                    float jt = std::min(vt / denom, friction * std::abs(jn));
                    body_a->linear_velocity = body_a->linear_velocity - tangent * (jt * body_a->inv_mass);
                    body_b->linear_velocity = body_b->linear_velocity + tangent * (jt * body_b->inv_mass);
                    Vec3 r1xt = r1.cross(tangent), r2xt = r2.cross(tangent);
                    body_a->angular_velocity = body_a->angular_velocity - (body_a->inv_inertia * r1xt) * jt;
                    body_b->angular_velocity = body_b->angular_velocity + (body_b->inv_inertia * r2xt) * jt;
                }
            }
        }

        // Position correction
        for (auto& c : contacts) {
            auto* body_a = get_body(c.body_a);
            auto* body_b = get_body(c.body_b);
            if (!body_a || !body_b) continue;
            if (body_a->is_static && body_b->is_static) continue;

            float slop = 0.005f;
            float correction = std::max(c.penetration - slop, 0.0f) * 0.4f;
            Vec3 corr = c.normal * correction;
            float total_inv = body_a->inv_mass + body_b->inv_mass;
            if (total_inv > EPS) {
                if (!body_a->is_static) body_a->position = body_a->position + corr * (body_a->inv_mass / total_inv);
                if (!body_b->is_static) body_b->position = body_b->position - corr * (body_b->inv_mass / total_inv);
            }
        }
    }

    void step(float dt) {
        dt = std::min(dt, 0.05f);

        for (auto& body : bodies) {
            if (body.is_static || body.inv_mass < EPS) continue;
            body.linear_velocity = body.linear_velocity + gravity * dt;
            body.linear_velocity = body.linear_velocity * (1.0f - linear_damping);
            body.angular_velocity = body.angular_velocity * (1.0f - angular_damping);

            body.position = body.position + body.linear_velocity * dt;

            float ang_len = body.angular_velocity.length();
            if (ang_len > EPS) {
                Vec3 axis = body.angular_velocity / ang_len;
                Quat dq = Quat::from_axis_angle(axis, ang_len * dt);
                body.rotation = (body.rotation * dq).normalized();
            }

            update_inertia(body);
        }

        contacts = detect_collisions();
        resolve_contacts();
    }

    float ray_vs_sphere(const Vec3& origin, const Vec3& dir, const RigidBody& body) {
        Vec3 oc = origin - body.position;
        float r = body.shape.params[0];
        float a = dir.dot(dir);
        float b = 2 * oc.dot(dir);
        float c = oc.dot(oc) - r * r;
        float disc = b*b - 4*a*c;
        if (disc < 0) return -1;
        return (-b - std::sqrt(disc)) / (2 * a);
    }

    float ray_vs_box(const Vec3& origin, const Vec3& dir, const RigidBody& body) {
        Vec3 local_origin = body.rotation.rotate(origin - body.position);
        Vec3 local_dir = body.rotation.rotate(dir);
        float hx = body.shape.params[0], hy = body.shape.params[1], hz = body.shape.params[2];

        float tmin = -FLT_MAX, tmax = FLT_MAX;
        for (int axis = 0; axis < 3; axis++) {
            float lo = (axis==0) ? local_origin.x : (axis==1) ? local_origin.y : local_origin.z;
            float ld = (axis==0) ? local_dir.x : (axis==1) ? local_dir.y : local_dir.z;
            float h = (axis==0) ? hx : (axis==1) ? hy : hz;
            if (std::abs(ld) < EPS) {
                if (lo < -h || lo > h) return -1;
            } else {
                float t1 = (-h - lo) / ld, t2 = (h - lo) / ld;
                if (t1 > t2) std::swap(t1, t2);
                tmin = std::max(tmin, t1); tmax = std::min(tmax, t2);
                if (tmin > tmax) return -1;
            }
        }
        return tmin > 0 ? tmin : tmax;
    }

    float ray_vs_capsule(const Vec3& origin, const Vec3& dir, const RigidBody& body) {
        float r = body.shape.params[0], hh = body.shape.params[1];
        Vec3 seg_a = body.position + body.rotation.rotate({0, -hh, 0});
        Vec3 seg_b = body.position + body.rotation.rotate({0, hh, 0});
        Vec3 seg = seg_b - seg_a;
        Vec3 oc = origin - seg_a;
        float seg_len_sq = seg.length_sq();
        if (seg_len_sq < EPS) return ray_vs_sphere(origin, dir, body);
        float t_seg = std::max(0.0f, std::min(1.0f, oc.dot(seg) / seg_len_sq));
        Vec3 closest = seg_a + seg * t_seg;
        Vec3 co = origin - closest;
        float a = dir.dot(dir);
        float b = 2 * co.dot(dir);
        float c = co.dot(co) - r * r;
        float disc = b*b - 4*a*c;
        if (disc < 0) return -1;
        return (-b - std::sqrt(disc)) / (2 * a);
    }

    float ray_vs_mesh(const Vec3& origin, const Vec3& dir, const RigidBody& body) {
        float best_t = -1;
        int n = (int)body.shape.mesh_indices.size() / 3;
        for (int i = 0; i < n; i++) {
            int i0 = body.shape.mesh_indices[i*3];
            int i1 = body.shape.mesh_indices[i*3+1];
            int i2 = body.shape.mesh_indices[i*3+2];
            Vec3 v0(body.shape.mesh_verts[i0*3], body.shape.mesh_verts[i0*3+1], body.shape.mesh_verts[i0*3+2]);
            Vec3 v1(body.shape.mesh_verts[i1*3], body.shape.mesh_verts[i1*3+1], body.shape.mesh_verts[i1*3+2]);
            Vec3 v2(body.shape.mesh_verts[i2*3], body.shape.mesh_verts[i2*3+1], body.shape.mesh_verts[i2*3+2]);

            v0 = body.position + body.rotation.rotate(v0);
            v1 = body.position + body.rotation.rotate(v1);
            v2 = body.position + body.rotation.rotate(v2);

            Vec3 e1 = v1 - v0, e2 = v2 - v0;
            Vec3 pv = dir.cross(e2);
            float det = e1.dot(pv);
            if (std::abs(det) < EPS) continue;
            float inv_det = 1.0f / det;
            Vec3 tv = origin - v0;
            float u = tv.dot(pv) * inv_det;
            if (u < 0 || u > 1) continue;
            Vec3 qv = tv.cross(e1);
            float v = dir.dot(qv) * inv_det;
            if (v < 0 || u + v > 1) continue;
            float t = e2.dot(qv) * inv_det;
            if (t < 0) continue;
            if (best_t < 0 || t < best_t) best_t = t;
        }
        return best_t;
    }

    float ray_vs_body(const Vec3& origin, const Vec3& dir, const RigidBody& body) {
        switch (body.shape.type) {
        case ShapeType::SPHERE:  return ray_vs_sphere(origin, dir, body);
        case ShapeType::BOX:     return ray_vs_box(origin, dir, body);
        case ShapeType::CAPSULE: return ray_vs_capsule(origin, dir, body);
        case ShapeType::MESH:    return ray_vs_mesh(origin, dir, body);
        default: return -1;
        }
    }

    Vec3 estimate_normal(const RigidBody& body, const Vec3& point) {
        switch (body.shape.type) {
        case ShapeType::SPHERE:
            return (point - body.position).normalized();
        case ShapeType::BOX: {
            Vec3 local = body.rotation.rotate(point - body.position);
            float hx = body.shape.params[0], hy = body.shape.params[1], hz = body.shape.params[2];
            float nx = std::copysignf(1.0f, local.x) * (std::abs(local.x) / hx);
            float ny = std::copysignf(1.0f, local.y) * (std::abs(local.y) / hy);
            float nz = std::copysignf(1.0f, local.z) * (std::abs(local.z) / hz);
            float mx = std::max({std::abs(nx), std::abs(ny), std::abs(nz)});
            Vec3 n_local;
            if (std::abs(nx) == mx) n_local = {std::copysignf(1.0f, nx), 0, 0};
            else if (std::abs(ny) == mx) n_local = {0, std::copysignf(1.0f, ny), 0};
            else n_local = {0, 0, std::copysignf(1.0f, nz)};
            return body.rotation.rotate(n_local);
        }
        default: return {0, 1, 0};
        }
    }

    RaycastHit raycast(const Vec3& origin, const Vec3& direction, float max_dist) {
        RaycastHit best;
        best.distance = max_dist;
        Vec3 dir = direction.normalized();

        for (auto& body : bodies) {
            if (body.shape.type == ShapeType::PLANE) continue;
            float t = ray_vs_body(origin, dir, body);
            if (t > 0 && t < best.distance) {
                best.hit = true;
                best.distance = t;
                best.point = origin + dir * t;
                best.normal = estimate_normal(body, best.point);
                best.body_id = body.id;
            }
        }
        return best;
    }

    void apply_force(int body_id, const Vec3& force, const Vec3& point) {
        auto* body = get_body(body_id);
        if (!body || body->is_static) return;
        body->linear_velocity = body->linear_velocity + force * body->inv_mass;
        Vec3 r = point - body->position;
        Vec3 torque = r.cross(force);
        body->angular_velocity = body->angular_velocity + (body->inv_inertia * torque);
    }

    ~PhysicsWorld() { bodies.clear(); contacts.clear(); }

    void clear() { bodies.clear(); contacts.clear(); next_id = 0; }
};

// =========================================================================
// Nanobind bindings
// =========================================================================

NB_MODULE(_physics, m) {
    nb::set_leak_warnings(false);
    nb::class_<Vec3>(m, "Vec3")
        .def(nb::init<>())
        .def(nb::init<float, float, float>())
        .def_rw("x", &Vec3::x).def_rw("y", &Vec3::y).def_rw("z", &Vec3::z)
        .def(nb::self + nb::self).def(nb::self - nb::self).def(nb::self * float()).def(nb::self / float()).def(-nb::self)
        .def("length", &Vec3::length).def("length_sq", &Vec3::length_sq)
        .def("normalized", &Vec3::normalized).def("dot", &Vec3::dot).def("cross", &Vec3::cross)
        .def("to_array", &Vec3::to_array).def("to_list", &Vec3::to_list).def("__repr__", &Vec3::repr)
        .def_static("zero", &Vec3::zero).def_static("up", &Vec3::up)
        .def_static("right", &Vec3::right).def_static("forward", &Vec3::forward).def_static("lerp", &Vec3::lerp);

    nb::class_<Quat>(m, "Quat")
        .def(nb::init<>()).def(nb::init<float, float, float, float>())
        .def_rw("w", &Quat::w).def_rw("x", &Quat::x).def_rw("y", &Quat::y).def_rw("z", &Quat::z)
        .def(nb::self * nb::self)
        .def("rotate", &Quat::rotate).def("normalized", &Quat::normalized)
        .def("to_array", &Quat::to_array).def("to_list", &Quat::to_list).def("__repr__", &Quat::repr)
        .def_static("identity", &Quat::identity).def_static("from_axis_angle", &Quat::from_axis_angle)
        .def_static("from_euler", &Quat::from_euler)
        .def("to_euler", &Quat::to_euler);

    nb::class_<CollisionShape>(m, "CollisionShape")
        .def(nb::init<>())
        .def_static("make_sphere", &CollisionShape::make_sphere)
        .def_static("make_box", &CollisionShape::make_box)
        .def_static("make_plane", &CollisionShape::make_plane)
        .def_static("make_capsule", &CollisionShape::make_capsule)
        .def_static("make_mesh", &CollisionShape::make_mesh);

    nb::class_<RaycastHit>(m, "RaycastHit")
        .def_ro("hit", &RaycastHit::hit)
        .def_ro("point", &RaycastHit::point)
        .def_ro("normal", &RaycastHit::normal)
        .def_ro("distance", &RaycastHit::distance)
        .def_ro("body_id", &RaycastHit::body_id);

    nb::class_<RigidBody>(m, "RigidBody")
        .def(nb::init<>())
        .def_rw("position", &RigidBody::position)
        .def_rw("rotation", &RigidBody::rotation)
        .def_rw("linear_velocity", &RigidBody::linear_velocity)
        .def_rw("angular_velocity", &RigidBody::angular_velocity)
        .def_rw("mass", &RigidBody::mass)
        .def_rw("is_static", &RigidBody::is_static)
        .def_rw("restitution", &RigidBody::restitution)
        .def_rw("friction", &RigidBody::friction)
        .def_rw("shape", &RigidBody::shape)
        .def_ro("id", &RigidBody::id)
        .def("set_mass", &RigidBody::set_mass)
        .def("set_static", &RigidBody::set_static);

    nb::class_<PhysicsWorld>(m, "PhysicsWorld")
        .def(nb::init<>())
        .def_rw("gravity", &PhysicsWorld::gravity)
        .def_rw("solver_iterations", &PhysicsWorld::solver_iterations)
        .def_rw("linear_damping", &PhysicsWorld::linear_damping)
        .def_rw("angular_damping", &PhysicsWorld::angular_damping)
        .def("add_body", &PhysicsWorld::add_body)
        .def("remove_body", &PhysicsWorld::remove_body)
        .def("get_body", &PhysicsWorld::get_body, nb::rv_policy::reference)
        .def("step", &PhysicsWorld::step)
        .def("apply_force", &PhysicsWorld::apply_force)
        .def("raycast", &PhysicsWorld::raycast)
        .def("clear", &PhysicsWorld::clear);
}
