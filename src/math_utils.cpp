#include <nanobind/nanobind.h>
#include <nanobind/operators.h>
#include <nanobind/ndarray.h>
#include <nanobind/stl/string.h>
#include <cmath>
#include <cstring>
#include <stdexcept>

namespace nb = nanobind;
using namespace nb::literals;

// =========================================================================
// Vector3
// =========================================================================

struct Vector3 {
    float x, y, z;

    Vector3() : x(0), y(0), z(0) {}
    Vector3(float x, float y, float z) : x(x), y(y), z(z) {}

    Vector3 operator+(const Vector3& o) const { return {x + o.x, y + o.y, z + o.z}; }
    Vector3 operator-(const Vector3& o) const { return {x - o.x, y - o.y, z - o.z}; }
    Vector3 operator*(float s) const { return {x * s, y * s, z * s}; }
    Vector3 operator-() const { return {-x, -y, -z}; }
    bool operator==(const Vector3& o) const { return x == o.x && y == o.y && z == o.z; }
    bool operator!=(const Vector3& o) const { return !(*this == o); }

    float length() const {
        return std::sqrt(x * x + y * y + z * z);
    }

    Vector3 normalized() const {
        float ln = length();
        if (ln == 0) return {0, 0, 0};
        return {x / ln, y / ln, z / ln};
    }

    float dot(const Vector3& o) const {
        return x * o.x + y * o.y + z * o.z;
    }

    Vector3 cross(const Vector3& o) const {
        return {
            y * o.z - z * o.y,
            z * o.x - x * o.z,
            x * o.y - y * o.x
        };
    }

    nb::list to_list() const {
        nb::list l;
        l.append(nb::float_(x));
        l.append(nb::float_(y));
        l.append(nb::float_(z));
        return l;
    }

    nb::ndarray<nb::numpy, float> to_array() const {
        float* data = new float[3]{x, y, z};
        nb::capsule owner(data, [](void* p) noexcept { delete[] static_cast<float*>(p); });
        return nb::ndarray<nb::numpy, float>(data, {3}, owner);
    }

    std::string repr() const {
        char buf[64];
        std::snprintf(buf, sizeof(buf), "(%.3f, %.3f, %.3f)", x, y, z);
        return buf;
    }

    static Vector3 zero() { return {0, 0, 0}; }
    static Vector3 one() { return {1, 1, 1}; }
    static Vector3 up() { return {0, 1, 0}; }
    static Vector3 right() { return {1, 0, 0}; }
    static Vector3 forward() { return {0, 0, -1}; }
    static Vector3 lerp(const Vector3& a, const Vector3& b, float t) {
        return a + (b - a) * t;
    }
};

// =========================================================================
// Matrix4 – stored row-major in a flat float[16]
// =========================================================================

struct Matrix4 {
    float m[16]; // row-major: m[row*4 + col]

    Matrix4() {
        identity_impl();
    }

    explicit Matrix4(const float* data) {
        std::memcpy(m, data, 16 * sizeof(float));
    }

    void identity_impl() {
        std::memset(m, 0, 16 * sizeof(float));
        m[0] = m[5] = m[10] = m[15] = 1.0f;
    }

    static Matrix4 identity() { return Matrix4(); }

    static Matrix4 translation(const Vector3& v) {
        Matrix4 mat;
        mat.m[3] = v.x;
        mat.m[7] = v.y;
        mat.m[11] = v.z;
        return mat;
    }

    static Matrix4 rotation_x(float angle) {
        float c = std::cos(angle), s = std::sin(angle);
        Matrix4 mat;
        mat.m[5] = c;  mat.m[6] = -s;
        mat.m[9] = s;  mat.m[10] = c;
        return mat;
    }

    static Matrix4 rotation_y(float angle) {
        float c = std::cos(angle), s = std::sin(angle);
        Matrix4 mat;
        mat.m[0] = c;  mat.m[2] = s;
        mat.m[8] = -s; mat.m[10] = c;
        return mat;
    }

    static Matrix4 rotation_z(float angle) {
        float c = std::cos(angle), s = std::sin(angle);
        Matrix4 mat;
        mat.m[0] = c;  mat.m[1] = -s;
        mat.m[4] = s;  mat.m[5] = c;
        return mat;
    }

    static Matrix4 scale(const Vector3& v) {
        Matrix4 mat;
        mat.m[0] = v.x;
        mat.m[5] = v.y;
        mat.m[10] = v.z;
        return mat;
    }

    static Matrix4 perspective(float fov, float aspect, float near_, float far_) {
        float f = 1.0f / std::tan(fov / 2.0f);
        Matrix4 mat;
        mat.m[0] = f / aspect;
        mat.m[5] = f;
        mat.m[10] = (far_ + near_) / (near_ - far_);
        mat.m[11] = (2.0f * far_ * near_) / (near_ - far_);
        mat.m[14] = -1.0f;
        mat.m[15] = 0.0f;
        return mat;
    }

    static Matrix4 look_at(const Vector3& eye, const Vector3& target, const Vector3& up) {
        Vector3 f = (target - eye).normalized();
        Vector3 s = f.cross(up).normalized();
        Vector3 u = s.cross(f);

        Matrix4 mat;
        mat.m[0]  = s.x; mat.m[1]  = s.y; mat.m[2]  = s.z;
        mat.m[3]  = -s.dot(eye);
        mat.m[4]  = u.x; mat.m[5]  = u.y; mat.m[6]  = u.z;
        mat.m[7]  = -u.dot(eye);
        mat.m[8]  = -f.x; mat.m[9] = -f.y; mat.m[10] = -f.z;
        mat.m[11] =  f.dot(eye);
        return mat;
    }

    Matrix4 operator*(const Matrix4& o) const {
        Matrix4 r;
        for (int i = 0; i < 4; i++) {
            for (int j = 0; j < 4; j++) {
                float sum = 0;
                for (int k = 0; k < 4; k++) {
                    sum += m[i*4 + k] * o.m[k*4 + j];
                }
                r.m[i*4 + j] = sum;
            }
        }
        return r;
    }

    Matrix4 inverse() const {
        const float* M = m;
        float A2323 = M[10] * M[15] - M[11] * M[14];
        float A1323 = M[9]  * M[15] - M[11] * M[13];
        float A1223 = M[9]  * M[14] - M[10] * M[13];
        float A0323 = M[8]  * M[15] - M[11] * M[12];
        float A0223 = M[8]  * M[14] - M[10] * M[12];
        float A0123 = M[8]  * M[13] - M[9]  * M[12];
        float A2313 = M[6]  * M[15] - M[7]  * M[14];
        float A1313 = M[5]  * M[15] - M[7]  * M[13];
        float A1213 = M[5]  * M[14] - M[6]  * M[13];
        float A2312 = M[6]  * M[11] - M[7]  * M[10];
        float A1312 = M[5]  * M[11] - M[7]  * M[9];
        float A1212 = M[5]  * M[10] - M[6]  * M[9];
        float A0313 = M[4]  * M[15] - M[7]  * M[12];
        float A0213 = M[4]  * M[14] - M[6]  * M[12];
        float A0312 = M[4]  * M[11] - M[7]  * M[8];
        float A0212 = M[4]  * M[10] - M[6]  * M[8];
        float A0113 = M[4]  * M[13] - M[5]  * M[12];
        float A0112 = M[4]  * M[9]  - M[5]  * M[8];

        float det = M[0] * (M[5] * A2323 - M[6] * A1323 + M[7] * A1223)
                  - M[1] * (M[4] * A2323 - M[6] * A0323 + M[7] * A0223)
                  + M[2] * (M[4] * A1323 - M[5] * A0323 + M[7] * A0123)
                  - M[3] * (M[4] * A1223 - M[5] * A0223 + M[6] * A0123);

        if (det == 0) throw std::runtime_error("Matrix is singular");

        float inv_det = 1.0f / det;
        Matrix4 r;
        r.m[0]  = inv_det *  (M[5] * A2323 - M[6] * A1323 + M[7] * A1223);
        r.m[1]  = inv_det * -(M[1] * A2323 - M[2] * A1323 + M[3] * A1223);
        r.m[2]  = inv_det *  (M[1] * A2313 - M[2] * A1313 + M[3] * A1213);
        r.m[3]  = inv_det * -(M[1] * A2312 - M[2] * A1312 + M[3] * A1212);
        r.m[4]  = inv_det * -(M[4] * A2323 - M[6] * A0323 + M[7] * A0223);
        r.m[5]  = inv_det *  (M[0] * A2323 - M[2] * A0323 + M[3] * A0223);
        r.m[6]  = inv_det * -(M[0] * A2313 - M[2] * A0313 + M[3] * A0213);
        r.m[7]  = inv_det *  (M[0] * A2312 - M[2] * A0312 + M[3] * A0212);
        r.m[8]  = inv_det *  (M[4] * A1323 - M[5] * A0323 + M[7] * A0123);
        r.m[9]  = inv_det * -(M[0] * A1323 - M[1] * A0323 + M[3] * A0123);
        r.m[10] = inv_det *  (M[0] * A1313 - M[1] * A0313 + M[3] * A0113);
        r.m[11] = inv_det * -(M[0] * A1312 - M[1] * A0312 + M[3] * A0112);
        r.m[12] = inv_det * -(M[4] * A1223 - M[5] * A0223 + M[6] * A0123);
        r.m[13] = inv_det *  (M[0] * A1223 - M[1] * A0223 + M[2] * A0123);
        r.m[14] = inv_det * -(M[0] * A1213 - M[1] * A0213 + M[2] * A0113);
        r.m[15] = inv_det *  (M[0] * A1212 - M[1] * A0212 + M[2] * A0112);
        return r;
    }

    Matrix4 transpose() const {
        Matrix4 r;
        for (int i = 0; i < 4; i++)
            for (int j = 0; j < 4; j++)
                r.m[i*4 + j] = m[j*4 + i];
        return r;
    }

    nb::ndarray<nb::numpy, float> get_data() const {
        float* data = new float[16];
        std::memcpy(data, m, 16 * sizeof(float));
        nb::capsule owner(data, [](void* p) noexcept { delete[] static_cast<float*>(p); });
        return nb::ndarray<nb::numpy, float>(data, {4, 4}, owner);
    }

    void set_data(nb::ndarray<nb::numpy, float> arr) {
        if (arr.ndim() != 2 || arr.shape(0) != 4 || arr.shape(1) != 4)
            throw std::runtime_error("data must be a 4x4 array");
        auto buf = arr.data();
        std::memcpy(m, buf, 16 * sizeof(float));
    }
};

// =========================================================================
// nanobind module
// =========================================================================

NB_MODULE(_math_utils, m) {
    nb::set_leak_warnings(false);
    nb::class_<Vector3>(m, "Vector3")
        .def(nb::init<>())
        .def(nb::init<float, float, float>(), "x"_a, "y"_a, "z"_a)
        .def_rw("x", &Vector3::x)
        .def_rw("y", &Vector3::y)
        .def_rw("z", &Vector3::z)
        .def(nb::self + nb::self)
        .def(nb::self - nb::self)
        .def(nb::self * float())
        .def(-nb::self)
        .def(nb::self == nb::self)
        .def(nb::self != nb::self)
        .def("__repr__", &Vector3::repr)
        .def("length", &Vector3::length)
        .def("normalized", &Vector3::normalized)
        .def("dot", &Vector3::dot)
        .def("cross", &Vector3::cross)
        .def("to_array", &Vector3::to_array)
        .def("to_list", &Vector3::to_list)
        .def_static("zero", &Vector3::zero)
        .def_static("one", &Vector3::one)
        .def_static("up", &Vector3::up)
        .def_static("right", &Vector3::right)
        .def_static("forward", &Vector3::forward)
        .def_static("lerp", &Vector3::lerp);

    nb::class_<Matrix4>(m, "Matrix4")
        .def(nb::init<>())
        .def("__init__", [](Matrix4* p, nb::ndarray<nb::numpy, float> data) {
            new (p) Matrix4(data.data());
        })
        .def_static("identity", &Matrix4::identity)
        .def_static("translation", &Matrix4::translation)
        .def_static("rotation_x", &Matrix4::rotation_x)
        .def_static("rotation_y", &Matrix4::rotation_y)
        .def_static("rotation_z", &Matrix4::rotation_z)
        .def_static("scale", &Matrix4::scale)
        .def_static("perspective", &Matrix4::perspective)
        .def_static("look_at", &Matrix4::look_at)
        .def(nb::self * nb::self)
        .def("inverse", &Matrix4::inverse)
        .def("transpose", &Matrix4::transpose)
        .def_prop_rw("data", &Matrix4::get_data, &Matrix4::set_data, nb::rv_policy::move);
}
