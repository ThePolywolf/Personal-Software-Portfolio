using Unity.Burst;
using Unity.Collections;
using Unity.Jobs;
using UnityEngine;

namespace Monsters
{
    [RequireComponent(typeof(MeshFilter), typeof(MeshRenderer))]
    public class NodeTrailMeshBuilder : MonoBehaviour
    {
        [SerializeField] private BodyConstructionSettings quality;
        [SerializeField] private NodeTrailSettings settings;

        private Transform[] _nodes;
        private MeshFilter _meshFilter;

        private int Rings => _nodes.Length;
        private int VertexCount => quality.ringVertexCount;

        private Vector3[] _vertices;
        private Vector3[] _normals;
        private NativeArray<Vector3> _nativeVertices;
        private NativeArray<Vector3> _nativeNormals;

        public void InitializeFromManager(Transform head, Transform[] nodes, NodeTrailSettings settingsIn)
        {
            _nodes = new Transform[nodes.Length + 1];
            _nodes[0] = head;
            for (var i = 0; i < nodes.Length; i++)
                _nodes[i + 1] = nodes[i];

            settings = settingsIn;
        }

        private void Awake()
        {
            _meshFilter = GetComponent<MeshFilter>();
            _meshFilter.mesh = new Mesh();
        }

        private void Start()
        {
            SetUpMesh();
            
            GenerateMeshVertices();
            GenerateMeshTriangles();
        }

        private void Update()
        {
            GenerateMeshVertices();
        }

        private void OnDestroy()
        {
            _nativeVertices.Dispose();
            _nativeNormals.Dispose();
        }

        private void GenerateMeshVertices()
        {
            if (_nodes.Length < 2)
                return;

            if (settings is null)
                return;
            
            GenerateMeshVertexAndNormals();
            _meshFilter.mesh.vertices = _vertices;
            _meshFilter.mesh.normals = _normals;
        }

        private void GenerateMeshTriangles()
        {
            _meshFilter.mesh.triangles = GetTriangles();
        }

        private void SetUpMesh()
        {
            _meshFilter.mesh.Clear();
            
            _vertices = new Vector3[Rings * VertexCount];
            _normals = new Vector3[_vertices.Length];
            
            _nativeVertices = new NativeArray<Vector3>(_vertices.Length, Allocator.Persistent);
            _nativeNormals = new NativeArray<Vector3>(_normals.Length, Allocator.Persistent);
            
            _meshFilter.mesh.MarkDynamic();
        }
        
        private void GenerateMeshVertexAndNormals()
        {
            // copy current vertices and normals
            _nativeVertices.CopyFrom(_vertices);
            _nativeNormals.CopyFrom(_normals);
            
            var positions = new NativeArray<Vector3>(_nodes.Length, Allocator.TempJob);
            var rotations = new NativeArray<Quaternion>(_nodes.Length, Allocator.TempJob);
            var curves = new NativeArray<float>(_nodes.Length, Allocator.TempJob);

            for (var i = 0; i < _nodes.Length; i++)
            {
                positions[i] = _nodes[i].position;
                rotations[i] = _nodes[i].rotation;
                curves[i] = settings.CurveEvaluation(i, Rings - 1);
            }

            try
            {
                // job system
                var meshJob = new UpdateMeshJob
                {
                    Vertices = _nativeVertices,
                    Normals = _nativeNormals,
                    Positions = positions,
                    Rotations = rotations,
                    Offset = settings.offset,
                    VertexCount = VertexCount,
                    Curves = curves
                };

                var handle = meshJob.Schedule(_vertices.Length, 64);
                handle.Complete();

                _nativeVertices.CopyTo(_vertices);
                _nativeNormals.CopyTo(_normals);

                _meshFilter.mesh.vertices = _vertices;
                _meshFilter.mesh.normals = _normals;
            }
            finally
            {
                positions.Dispose();
                rotations.Dispose();
                curves.Dispose();
            }
        }
        
        [BurstCompile]
        private struct UpdateMeshJob : IJobParallelFor
        {
            public NativeArray<Vector3> Vertices;
            public NativeArray<Vector3> Normals;
            [ReadOnly] public NativeArray<Vector3> Positions;
            [ReadOnly] public NativeArray<Quaternion> Rotations;
            [ReadOnly] public NativeArray<float> Curves;

            [ReadOnly] public Vector3 Offset;
            [ReadOnly] public int VertexCount;

            public void Execute(int index)
            {
                var ringIndex = index / VertexCount;
                var vertexIndex = index % VertexCount;
                
                var rotationPointer = Quaternion.Euler(0, 0, 360f / VertexCount * vertexIndex);
                var pointer = Rotations[ringIndex] * rotationPointer * Vector3.up;
                
                Vertices[index] = Positions[ringIndex] + Offset + pointer * Curves[ringIndex];
                Normals[index] = pointer.normalized;
            }
        }

        private int[] GetTriangles()
        {
            // 4 faces per segment, 2 faces per end, 2 triangles per face, 3 vert. indexes per triangle
            var endTriangleCount = VertexCount * (Rings - 1) * 2;
            var triangles = new int[endTriangleCount * 6];
            
            // segment faces
            for (var segment = 0; segment < Rings - 1; segment++)
            {
                var faceIndex = segment * VertexCount;
            
                var nearIndexOrder = new int[VertexCount];
                for (var i = 0; i < nearIndexOrder.Length; i++)
                    nearIndexOrder[i] = i + faceIndex;
                
                var farIndexOrder = new int[VertexCount];
                for (var i = 0; i < farIndexOrder.Length; i++)
                    farIndexOrder[i] = i + faceIndex + VertexCount;
                
                for (var face = 0; face < VertexCount; face++)
                {
                    var i2 = (face + 1) % VertexCount;
                    FaceTriangles(ref triangles, faceIndex + face, nearIndexOrder[i2], nearIndexOrder[face], farIndexOrder[face], farIndexOrder[i2]);
                }
            }
            
            return triangles;
        }

        /// <summary>
        /// Returns the triangles that make up the given face indexes. a, b, c, and d must be in clockwise order
        /// </summary>
        /// <param name="triangles">reference array to add to</param>
        /// <param name="faceIndex">index of the triangle data to place (multiplied by 6 to get vertex index)</param>
        private static void FaceTriangles(ref int[] triangles, int faceIndex, int a, int b, int c, int d)
        {
            var order = new[] {a, b, c, c, d, a};
            
            for (var i = 0; i < 6; i++)
                triangles[faceIndex * 6 + i] = order[i];
        }
    }
}
