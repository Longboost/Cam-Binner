from sys import argv
from struct import pack, unpack_from
import xml.etree.ElementTree as ET

class CamBin:
    
    # data arrays
    CameraData = []
    CurveData = []
    ShapeData = []
    FaceData = []
    PointData = []
    VtxIdxData = []
    AreaData = []
    
    AnimCurveData = [] # what is this?! there's no total stored for these
    
    # pad value?
    Unknown2 = Unknown3 = int(0xFFBF0EEC)

    def readString(self, src: bytearray) -> str:
        string = src[:src.index(b'\x00')]
        return string
    
    class Camera:
        # example values
        verticalFieldOfView = 25.0
        
        nearClipPlane = 1.0
        farClipPlane = 500.0
    
    class Curve:
        # example values
        Name = '|GG4G_CameraRoad|curve1'
        
        StartPointIdx = 1
        EndPointIdx = 1
        
        L_Width = 0.0
        R_Width = 0.0
        
        Start_Clip = 0.0
        End_Clip = 1.0
        
        Cam_Distance = 40.0
        Cam_Height_Angle = 12.0
        Cam_LookUp_Angle = -8.0
        Cam_LR_Shift = 20.0
        
        EnableLocalClip = True
        EnableGlobalClip = False
        
        EnableFixY = False
        Cam_FixY = 0.0
        
        Cam_Curve2D = False
        Cam_Curve3D = False
        
        BoundingBox = (-60.1, -0.1, -5.1, 130.1, 0.1, -4.9)
        
        InfoPoint = (0, 8)
        InfoShape = (0, 1)
        InfoArea = (0, 0)
    
    class Shape:
        # example values
        Name = 'pPlane1'
        BoundingBox = (-80.10000246, -10.1, -10.1, 141.1000015, -9.9, 5.1)
        InfoVtx = (0, 4)
        InfoFace = (0, 1)
    
    def __init__(self, src: bytearray = None):
        
        if src is None:
            # if we aren't importing a file, exit before doing anything
            return
        
        readOff = 0
        
        # file length bytes (not needed for conversion to xml)
        readOff += 4
        
        self.ConverterName = self.readString(src[readOff:readOff+64])
        readOff += 64
        self.ConverterName = self.ConverterName.decode('utf-8')
        
        self.ConverterVersion = self.readString(src[readOff:readOff+64])
        readOff += 64
        self.ConverterVersion = self.ConverterVersion.decode('utf-8')

        self.ConvertDate = self.readString(src[readOff:readOff+64])
        readOff += 64
        self.ConvertDate = self.ConvertDate.decode('utf-8')
        
        self.TotalCamera, self.TotalCurve, self.TotalShape, self.TotalFace, self.TotalPoint, self.TotalVtx, self.TotalVtxIdx, self.TotalArea, self.Unknown = unpack_from('>9I', src, offset=readOff)
        readOff += 36
        
        assert self.TotalArea == 0, '"Area" objects are not supported!!'
        assert self.Unknown == 0, 'Unknown bytes before objects are not 0 – tell Longboost to look into this!'
        
        readOff_tmp = unpack_from('>I', src, offset=readOff)[0]
        readOff += 4
        for _ in range(self.TotalCamera):
            
            camera = self.Camera()
            camera.verticalFieldOfView, camera.nearClipPlane, camera.farClipPlane = unpack_from('>3f', src, offset=readOff_tmp)
            
            self.CameraData.append(camera)
        
        readOff_tmp = unpack_from('>I', src, offset=readOff)[0]
        readOff += 4
        for _ in range(self.TotalCurve):
            
            curve = self.Curve()
            
            curve.Name = self.readString(src[readOff_tmp:readOff_tmp+64])
            readOff_tmp += 64
            curve.Name = curve.Name.decode('utf-8')
            
            (
                curve.StartPointIdx, # int
                curve.EndPointIdx, # int 
                
                curve.L_Width, # float
                curve.R_Width, # float
                
                curve.Start_Clip, # float
                curve.End_Clip, # float
                
                curve.Cam_Distance, # float
                curve.EnableFixY, # bool
                curve.Cam_FixY, # float
                curve.Cam_Height_Angle, #float
                curve.Cam_LookUp_Angle, #float
                curve.Cam_Curve2D, # bool
                curve.Cam_Curve3D, # bool
                curve.Cam_LR_Shift, # float
                
                curve.EnableGlobalClip, # bool
                curve.EnableLocalClip # bool
            ) = unpack_from('>2I 5f 3x? 2f 8x f 3x? 3x? f 3x? 3x? ', src, offset=readOff_tmp)
            
            pointCount = curve.EndPointIdx - curve.StartPointIdx
            #assert pointCount <= 1, f'More than 1 point in curve "{curve.Name}" ({pointCount}) – tell Longboost to look into this!'
            
            readOff_tmp += 72
            
            curve.BoundingBox = unpack_from('>6f', src, offset=readOff_tmp)
            readOff_tmp += 24
            
            curve.InfoPoint = unpack_from('>2I', src, offset=readOff_tmp)
            readOff_tmp += 8

            print(curve.Name)
            print(hex(readOff_tmp))
            
            curve.InfoShape = unpack_from('>2I', src, offset=readOff_tmp)
            readOff_tmp += 8
            
            curve.InfoArea = unpack_from('>2I', src, offset=readOff_tmp)
            readOff_tmp += 8
            
            self.CurveData.append(curve)
        
        readOff_tmp = unpack_from('>I', src, offset=readOff)[0]
        readOff += 4
        for _ in range(self.TotalShape):
            
            shape = self.Shape()
            
            shape.Name = self.readString(src[readOff_tmp:readOff_tmp+64])
            readOff_tmp += 64
            shape.Name = shape.Name.decode('utf-8')
            
            shape.BoundingBox = unpack_from('>6f', src, offset=readOff_tmp)
            readOff_tmp += 24
            
            shape.InfoVtx = unpack_from('>2I', src, offset=readOff_tmp)
            readOff_tmp += 8
            
            shape.InfoFace = unpack_from('>2I', src, offset=readOff_tmp)
            readOff_tmp += 8
            
            self.ShapeData.append(shape)
        
        # FaceData
        readOff_tmp = unpack_from('>I', src, offset=readOff)[0]
        readOff += 4
        readOff_tmp_end = readOff_tmp + (self.TotalFace * 8)
        self.FaceData = [unpack_from('>2I', src, readOff_tmp) for readOff_tmp in range(readOff_tmp, readOff_tmp_end, 8)]

        # PointData
        readOff_tmp = unpack_from('>I', src, offset=readOff)[0]
        readOff += 4
        readOff_tmp_end = readOff_tmp + (self.TotalPoint * 12)
        self.PointData = [unpack_from('>3f', src, readOff_tmp) for readOff_tmp in range(readOff_tmp, readOff_tmp_end, 12)]
        
        # VtxData
        readOff_tmp = unpack_from('>I', src, offset=readOff)[0]
        readOff += 4
        readOff_tmp_end = readOff_tmp + (self.TotalVtx * 12)
        self.VtxData = [unpack_from('>3f', src, readOff_tmp) for readOff_tmp in range(readOff_tmp, readOff_tmp_end, 12)]
        
        # VtxIdxData
        readOff_tmp = unpack_from('>I', src, offset=readOff)[0]
        readOff += 4
        readOff_tmp_end = readOff_tmp + (self.TotalVtxIdx * 4)
        self.VtxIdxData = [unpack_from('>I', src, readOff_tmp)[0] for readOff_tmp in range(readOff_tmp, readOff_tmp_end, 4)]
        
        self.Unknown2, self.Unknown3 = unpack_from('>2I', src, offset=readOff)
        assert self.Unknown2 == int(0xFFBF0EEC), f'Unknown2 did not have expected value of 0xFFBF0EEC, instead it had {hex(self.Unknown2)} – tell Longboost to look into this!'
        assert self.Unknown2 == self.Unknown3, 'Unknown2 and Unknown3 differ – tell Longboost to look into this!'
    
    def writeToSrc(self) -> bytearray:
        def appendString(string: str):
            nonlocal src
            string = string.encode('utf-8')
            string += b'\x00' * (64 - len(string))
            src.extend(string)
        
        def overwriteChunk(address: int, chunk: bytearray):
            nonlocal src
            src = src[:address] + chunk + src[address + 4:]
        
        src = bytearray()
        
        # these first four bytes will be filled with the file's length later.
        src.extend(b'\x00\x00\x00\x00')
        
        appendString(self.ConverterName)
        appendString(self.ConverterVersion)
        appendString(self.ConvertDate)
        
        src.extend(pack(
            '>8I', 
            self.TotalCamera,
            self.TotalCurve,
            self.TotalShape,
            self.TotalFace,
            self.TotalPoint,
            self.TotalVtx,
            self.TotalVtxIdx,
            self.TotalArea
        ))
        
        # unknown
        src.extend(b'\x00\x00\x00\x00')
        
        # object list addresses: will get filled in later
        listAddressesStart = len(src)
        src.extend(b'\x00\x00\x00\x00' * 7)
        
        # unknown – padding values, maybe?
        src.extend(pack('>2I', self.Unknown2, self.Unknown3))
        
        # cameras
        overwriteChunk(listAddressesStart, pack('>I', len(src)))
        for cam in self.CameraData:
            src.extend(pack(
                '>3f', 
                cam.verticalFieldOfView, 
                cam.nearClipPlane, 
                cam.farClipPlane
            ))
        
        # curves
        overwriteChunk(listAddressesStart + 4, pack('>I', len(src)))
        for curve in self.CurveData:
            appendString(curve.Name)
            src.extend(pack(
                '>2I 5f 3x? 2f 8x f 3x? 3x? f 3x? 3x?',
                curve.StartPointIdx, # int
                curve.EndPointIdx, # int 
                
                curve.L_Width, # float
                curve.R_Width, # float
                
                curve.Start_Clip, # float
                curve.End_Clip, # float
                
                curve.Cam_Distance, # float
                curve.EnableFixY, # bool
                curve.Cam_FixY, # float
                curve.Cam_Height_Angle, #float
                curve.Cam_LookUp_Angle, #float
                curve.Cam_Curve2D, # bool
                curve.Cam_Curve3D, # bool
                curve.Cam_LR_Shift, # float
                
                curve.EnableGlobalClip, # bool
                curve.EnableLocalClip # bool
            ))
            src.extend(pack('>6f', *curve.BoundingBox))
            src.extend(pack('>2I', *curve.InfoPoint))
            src.extend(pack('>2I', *curve.InfoShape))
            src.extend(pack('>2I', *curve.InfoArea))
        
        # shapes
        overwriteChunk(listAddressesStart + 8, pack('>I', len(src)))
        for shape in self.ShapeData:
            appendString(shape.Name)
            src.extend(pack('>6f', *shape.BoundingBox))
            src.extend(pack('>2I', *shape.InfoVtx))
            src.extend(pack('>2I', *shape.InfoFace))
        
        # faces
        overwriteChunk(listAddressesStart + 12, pack('>I', len(src)))
        for face in self.FaceData:
            src.extend(pack('>2I', *face))
        
        # points
        overwriteChunk(listAddressesStart + 16, pack('>I', len(src)))
        for point in self.PointData:
            src.extend(pack('>3f', *point))
        
        # vtxs
        overwriteChunk(listAddressesStart + 20, pack('>I', len(src)))
        for vtx in self.VtxData:
            src.extend(pack('>3f', *vtx))
        
        # vtxidxs
        overwriteChunk(listAddressesStart + 24, pack('>I', len(src)))
        src.extend(pack(f'>{len(self.VtxIdxData)}I', *self.VtxIdxData))
        
        # finally we insert the file length into the first 4 bytes
        overwriteChunk(0, pack('>I', len(src)))
        
        return src

def Export(file: CamBin, filename: str):
    
    spaceChar = "\t"
    
    def addSub(parent, name: str, value, manualIndent : int = 2) -> ET.SubElement:
    # before adding a subelement, we need to format the datatype for readability
        
        # strings
        if type(value) is str:
            value = f'"{value}"'
        
        # arrays
        elif type(value) is tuple or type(value) is list:
            # test for 2d array
            if len(value) > 0 and type(value[0]) is tuple:
                value = [' '.join([str(y) for y in x]) for x in value]
                value = f'\n{spaceChar * manualIndent}'.join([str(x) for x in value])
            else:
                value = ' '.join([str(x) for x in value])
        
        s = ET.SubElement(parent, name)
        
        if not value is None:
            s.text = f'\n{spaceChar * manualIndent}{value}\n{spaceChar * (manualIndent-1)}'
        return s
    
    xml = ET.Element('CameraRoad')
    
    addSub(xml, 'ConverterName', file.ConverterName)
    addSub(xml, 'ConverterVersion', file.ConverterVersion)
    addSub(xml, 'ConvertDate', file.ConvertDate)
    
    addSub(xml, 'TotalCamera', file.TotalCamera)
    addSub(xml, 'TotalCurve', file.TotalCurve)
    addSub(xml, 'TotalShape', file.TotalShape)
    addSub(xml, 'TotalFace', file.TotalFace)
    addSub(xml, 'TotalPoint', file.TotalPoint)
    addSub(xml, 'TotalVtx', file.TotalVtx)
    addSub(xml, 'TotalVtxIdx', file.TotalVtxIdx)
    addSub(xml, 'TotalArea', file.TotalArea)
    
    cameras = addSub(xml, 'CameraData', None)
    for cam in file.CameraData:
        camElement = addSub(cameras, 'Camera', None)
        addSub(camElement, 'verticalFieldOfView', cam.verticalFieldOfView, 4)
        addSub(camElement, 'nearClipPlane', cam.nearClipPlane, 4)
        addSub(camElement, 'farClipPlane', cam.farClipPlane, 4)
    
    curves = addSub(xml, 'CurveData', None)
    for curve in file.CurveData:
        curveElement = addSub(curves, 'Curve', None)
        addSub(curveElement, 'Name', curve.Name, 4)
        addSub(curveElement, 'StartPointIdx', curve.StartPointIdx, 4)
        addSub(curveElement, 'EndPointIdx', curve.EndPointIdx, 4)
        addSub(curveElement, 'L_Width', curve.L_Width, 4)
        addSub(curveElement, 'R_Width', curve.R_Width, 4)
        addSub(curveElement, 'Start_Clip', curve.Start_Clip, 4)
        addSub(curveElement, 'End_Clip', curve.End_Clip, 4)
        addSub(curveElement, 'Cam_Distance', curve.Cam_Distance, 4)
        addSub(curveElement, 'Cam_Height_Angle', curve.Cam_Height_Angle, 4)
        addSub(curveElement, 'Cam_LookUp_Angle', curve.Cam_LookUp_Angle, 4)
        addSub(curveElement, 'Cam_LR_Shift', curve.Cam_LR_Shift, 4)
        addSub(curveElement, 'EnableLocalClip', curve.EnableLocalClip, 4)
        addSub(curveElement, 'EnableGlobalClip', curve.EnableGlobalClip, 4)
        addSub(curveElement, 'EnableFixY', curve.EnableFixY, 4)
        addSub(curveElement, 'Cam_FixY', curve.Cam_FixY, 4)
        addSub(curveElement, 'Cam_Curve2D', curve.Cam_Curve2D, 4)
        addSub(curveElement, 'Cam_Curve3D', curve.Cam_Curve3D, 4)
        addSub(curveElement, 'BoundingBox', curve.BoundingBox, 4)
        addSub(curveElement, 'InfoPoint', curve.InfoPoint, 4)
        addSub(curveElement, 'InfoShape', curve.InfoShape, 4)
        addSub(curveElement, 'InfoArea', curve.InfoArea, 4)
    
    shapes = addSub(xml, 'ShapeData', None)
    for shape in file.ShapeData:
        shapeElement = addSub(shapes, 'Shape', None)
        addSub(shapeElement, 'Name', shape.Name, 4)
        addSub(shapeElement, 'BoundingBox', shape.BoundingBox, 4)
        addSub(shapeElement, 'InfoVtx', shape.InfoVtx, 4)
        addSub(shapeElement, 'InfoFace', shape.InfoFace, 4)
    
    addSub(xml, 'FaceData', file.FaceData)
    addSub(xml, 'PointData', file.PointData)
    addSub(xml, 'VtxData', file.VtxData)
    addSub(xml, 'VtxIdxData', file.VtxIdxData)
    addSub(xml, 'AreaData', file.AreaData)
    addSub(xml, 'AnimCurveData', file.AnimCurveData)
    
    ET.indent(xml, space=spaceChar, level=0)
    
    print(ET.tostringlist(xml))
    open(filename, 'w').write(ET.tostring(xml).decode('utf-8'))

def Import(etree: ET.ElementTree) -> CamBin:
    # xmls' "text" fields only store strings, so we need to convert them to appropiate data types.
    def formatValue(value, layeredArray: bool = False):
        # string
        if '"' in value:
            value = value[value.index('"') + 1:]
            value = value[:value.index('"')]
        # bools
        elif 'True' in value:
            value = True
        elif 'False' in value:
            value = False
        else:
            # array
            if layeredArray:
                value = value.split('\n')
                value = [x.split() for x in value if x.split()] # using implicit booleaness of lists to check if they are empty, and omitting them if so.
                value = [[float(x) if '.' in x else int(x) for x in y] for y in value]
            else:
                value = value.split()
                value = [float(x) if '.' in x else int(x) for x in value]
                if len(value) == 1:
                    value = value[0]
        
        return value
    
    cambin = CamBin()
    root = etree.getroot()

    cambin.ConverterName = formatValue(root.find('ConverterName').text)
    cambin.ConverterVersion = formatValue(root.find('ConverterVersion').text)
    cambin.ConvertDate = formatValue(root.find('ConvertDate').text)
    cambin.TotalCamera = formatValue(root.find('TotalCamera').text)
    cambin.TotalCurve = formatValue(root.find('TotalCurve').text)
    cambin.TotalShape = formatValue(root.find('TotalShape').text)
    cambin.TotalFace = formatValue(root.find('TotalFace').text)
    cambin.TotalPoint = formatValue(root.find('TotalPoint').text)
    cambin.TotalVtx = formatValue(root.find('TotalVtx').text)
    cambin.TotalVtxIdx = formatValue(root.find('TotalVtxIdx').text)
    cambin.TotalArea = formatValue(root.find('TotalArea').text)
    
    cams = root.find('CameraData').findall('Camera')
    for camElement in cams:
        cam = cambin.Camera()
        
        cam.verticalFieldOfView = formatValue(camElement.find('verticalFieldOfView').text)
        cam.nearClipPlane = formatValue(camElement.find('nearClipPlane').text)
        cam.farClipPlane = formatValue(camElement.find('farClipPlane').text)
        
        cambin.CameraData.append(cam)

    curves = root.find('CurveData').findall('Curve')
    for curveElement in curves:
        curve = cambin.Curve()
        
        curve.Name = formatValue(curveElement.find('Name').text)
        curve.StartPointIdx = formatValue(curveElement.find('StartPointIdx').text)
        curve.EndPointIdx = formatValue(curveElement.find('EndPointIdx').text)
        curve.L_Width = formatValue(curveElement.find('L_Width').text)
        curve.R_Width = formatValue(curveElement.find('R_Width').text)
        curve.Start_Clip = formatValue(curveElement.find('Start_Clip').text)
        curve.End_Clip = formatValue(curveElement.find('End_Clip').text)
        curve.Cam_Distance = formatValue(curveElement.find('Cam_Distance').text)
        curve.Cam_Height_Angle = formatValue(curveElement.find('Cam_Height_Angle').text)
        curve.Cam_LookUp_Angle = formatValue(curveElement.find('Cam_LookUp_Angle').text)
        curve.Cam_LR_Shift = formatValue(curveElement.find('Cam_LR_Shift').text)
        curve.EnableLocalClip = formatValue(curveElement.find('EnableLocalClip').text)
        curve.EnableGlobalClip = formatValue(curveElement.find('EnableGlobalClip').text)
        curve.EnableFixY = formatValue(curveElement.find('EnableFixY').text)
        curve.Cam_FixY = formatValue(curveElement.find('Cam_FixY').text)
        curve.Cam_Curve2D = formatValue(curveElement.find('Cam_Curve2D').text)
        curve.Cam_Curve3D = formatValue(curveElement.find('Cam_Curve3D').text)
        curve.BoundingBox = formatValue(curveElement.find('BoundingBox').text)
        curve.InfoPoint = formatValue(curveElement.find('InfoPoint').text)
        curve.InfoShape = formatValue(curveElement.find('InfoShape').text)
        curve.InfoArea = formatValue(curveElement.find('InfoArea').text)
        
        cambin.CurveData.append(curve)
    
    shapes = root.find('ShapeData').findall('Shape')
    for shapeElement in shapes:
        shape = cambin.Shape()
        
        shape.Name = formatValue(shapeElement.find('Name').text)
        shape.BoundingBox = formatValue(shapeElement.find('BoundingBox').text)
        shape.InfoVtx = formatValue(shapeElement.find('InfoVtx').text)
        shape.InfoFace = formatValue(shapeElement.find('InfoFace').text)
        
        cambin.ShapeData.append(shape)
    
    cambin.FaceData = formatValue(root.find('FaceData').text, True)
    cambin.PointData = formatValue(root.find('PointData').text, True)
    cambin.VtxData = formatValue(root.find('VtxData').text, True)
    cambin.VtxIdxData = formatValue(root.find('VtxIdxData').text, False)
    cambin.AreaData = formatValue(root.find('AreaData').text, False)
    cambin.AnimCurveData = formatValue(root.find('AnimCurveData').text, False)
    
    return cambin
    

def init():
    userNeedHelp = True
    for arg in argv[1:]:
        if arg.endswith('.cam.bin'):
            userNeedHelp = False
            file = CamBin(open(arg, 'rb').read())
            filename = f'{arg[:-4]}.xml'
            Export(file, filename)
        elif arg.endswith('.xml'):
            userNeedHelp = False
            file = Import(ET.parse(arg))
            output = file.writeToSrc()
            filename = f'{arg[:-4]}_output.bin'
            open(filename, 'wb').write(output)
    
    if userNeedHelp:
        print('Usage: \n  main.py <filename.cam.bin / filename.xml>')

if __name__ == '__main__':
    init()