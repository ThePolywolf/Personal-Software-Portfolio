using UnityEngine;

[RequireComponent(typeof(MeshFilter), typeof(MeshRenderer))]
public class TestMeshBuilder : MonoBehaviour
{
    [SerializeField] private float size;
    [Min(4)] [SerializeField] private int vertexCount;
    [SerializeField] private Vector3[] segmentRotations;
    [SerializeField] private AnimationCurve scaleCurve;
    [SerializeField] private float zStretch;
    
    private int Segments => segmentRotations.Length;
    
    private MeshFilter _meshFilter;

    private void Awake()
    {
        _meshFilter = GetComponent<MeshFilter>();
    }

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        _meshFilter.mesh = new Mesh();
        BuildMesh();
    }

    private Vector3[] GetVertices(out Vector3[] normalsOut)
    {
        // 4 vertices per slice, with 4 per end for sharp ends
        var vertices = new Vector3[Segments * vertexCount];
        var normals = new Vector3[vertices.Length];
        
        var rotationPointer = Quaternion.Euler(0, 0, 0);
        var rotationAmount = Quaternion.Euler(0, 0, -360f / vertexCount);
        
        // segment vertices
        for (var z = 0; z < Segments; z++)
        {
            for (var c = 0; c < vertexCount; c++)
            {
                var pointer = Quaternion.Euler(segmentRotations[z]) * rotationPointer * Vector3.up;
                var index = z * vertexCount + c;
                var segmentSize = size * scaleCurve.Evaluate((float)z / (Segments - 1));
                vertices[index] = new Vector3(0, 0, z * zStretch) + pointer * segmentSize;
                normals[index] = pointer;
                
                rotationPointer *= rotationAmount;
            }
        }

        normalsOut = normals;
        return vertices;
    }

    private int[] GetTriangles()
    {
        // 4 faces per segment, 2 faces per end, 2 triangles per face, 3 vert. indexes per triangle
        var endTriangleCount = vertexCount * (Segments - 1) * 2;
        var triangles = new int[endTriangleCount * 6];
        
        // segment faces
        for (var segment = 0; segment < Segments - 1; segment++)
        {
            var faceIndex = segment * vertexCount;
        
            var nearIndexOrder = new int[vertexCount];
            for (var i = 0; i < nearIndexOrder.Length; i++)
                nearIndexOrder[i] = i + faceIndex;
            
            var farIndexOrder = new int[vertexCount];
            for (var i = 0; i < farIndexOrder.Length; i++)
                farIndexOrder[i] = i + faceIndex + vertexCount;
            
            for (var face = 0; face < vertexCount; face++)
            {
                var i2 = (face + 1) % vertexCount;
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
    private void FaceTriangles(ref int[] triangles, int faceIndex, int a, int b, int c, int d)
    {
        var order = new[] {a, b, c, c, d, a};
        
        for (var i = 0; i < 6; i++)
            triangles[faceIndex * 6 + i] = order[i];
    }

    // Update is called once per frame
    void FixedUpdate()
    {
        BuildMesh();
    }

    private void BuildMesh()
    {
        if (Segments < 2)
            return;
        
        _meshFilter.mesh.Clear();
        
        _meshFilter.mesh.vertices = GetVertices(out var normalsOut);
        _meshFilter.mesh.triangles = GetTriangles();
        _meshFilter.mesh.normals = normalsOut;
    }
}
