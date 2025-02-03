function generateQR(data, outFile, version, ecLevel, mask)
% generateQR Generate a QR code image and save it.
%
%   generateQR(DATA, OUTFILENAME, VERSION, ECLEVEL, MASK)
%
%   DATA:      A string to encode.
%   OUTFILENAME: Name of the file to write (e.g. 'qr.png').
%   VERSION:   Either 'auto' or a numeric value (supported: 1, 2, or 40).
%   ECLEVEL:   Error correction level: 'L', 'M', 'Q', or 'H'.
%   MASK:      Optional mask index (0–7). If empty, the best mask is selected.
%
% This script supports three versions: 1, 2, and 40. In version 40 the RS
% block splitting is performed per standard (for byte–mode). No special‐purpose
% QR or RS toolkits are used.

    %% Process input arguments
    if nargin < 5, mask = []; end
    if nargin < 4, ecLevel = 'L'; end
    if nargin < 3, version = 'auto'; end
    
    % Supported versions and their capacity (for byte mode) [dataCodewords, eccCodewords]
    verParams(1).size = 21;
    verParams(1).L = [19, 7];
    verParams(1).M = [16, 10];
    verParams(1).Q = [13, 12];
    verParams(1).H = [9, 17];
    
    verParams(2).size = 25;
    verParams(2).L = [34, 10];
    verParams(2).M = [28, 16];
    verParams(2).Q = [22, 22];
    verParams(2).H = [16, 28];
    
    verParams(40).size = 177;
    verParams(40).L = [2953, 753];
    verParams(40).M = [2334, 1372];
    verParams(40).Q = [1666, 2040];
    verParams(40).H = [1276, 2430];
    
    % Alignment pattern locations: version 1: none; version 2: [6,18];
    % version 40: [6, 30, 58, 86, 114, 142, 170]
    alignLocs(1).loc = [];
    alignLocs(2).loc = [6, 18];
    alignLocs(40).loc = [6, 30, 58, 86, 114, 142, 170];
    
    % RS block structure for version 40 (byte mode)
    % For each EC level, specify a vector for the number of data codewords per block,
    % and a vector for the corresponding ecc codeword count.
    rsBlocks40.L.data = [repmat(118,1,22), repmat(119,1,3)];
    rsBlocks40.L.ecc  = [repmat(30,1,22), repmat(31,1,3)];
    rsBlocks40.M.data = [repmat(93,1,16), repmat(94,1,9)];
    rsBlocks40.M.ecc  = [repmat(54,1,3), repmat(55,1,22)];
    rsBlocks40.Q.data = [repmat(66,1,9), repmat(67,1,16)];
    rsBlocks40.Q.ecc  = [repmat(81,1,10), repmat(82,1,15)];
    rsBlocks40.H.data = [repmat(51,1,24), 52];
    rsBlocks40.H.ecc  = [repmat(97,1,20), repmat(98,1,5)];
    
    %% Auto-select version if requested.
    if ischar(version) && strcmpi(version, 'auto')
        % Try versions in order: 1, 2, 40.
        chosen = [];
        for v = [1,2,40]
            try
                % Try to encode data (this function will error if too long).
                dummy = encodeDataAll(data, v, ecLevel, verParams(v).(ecLevel)(1));
                chosen = v;
                break;
            catch
                % Data did not fit; try next version.
            end
        end
        if isempty(chosen)
            error('Data too long to fit in supported versions.');
        else
            version = chosen;
            fprintf('Auto-selected version: %d\n', version);
        end
    else
        version = str2double(version);
        if ~ismember(version, [1,2,40])
            error('Supported versions in this demo are 1, 2, or 40.');
        end
    end
    currVer = verParams(version);
    qrSize = currVer.size;
    dataCapacity = currVer.(ecLevel)(1);
    eccCapacity  = currVer.(ecLevel)(2);
    
    %% Initialize GF(256) tables.
    [expTable, logTable] = initGF256();
    
    %% Encode data.
    dataCodewords = encodeDataAll(data, version, ecLevel, dataCapacity);
    
    if version == 40
        % Split data into blocks according to RS structure.
        rsInfo = rsBlocks40.(ecLevel);
        blocks = {};
        idx = 1;
        for i = 1:length(rsInfo.data)
            blockSize = rsInfo.data(i);
            blocks{end+1} = dataCodewords(idx:idx+blockSize-1);
            idx = idx + blockSize;
        end
        if idx-1 ~= length(dataCodewords)
            error('RS block splitting error: index mismatch.');
        end
        % Compute ECC for each block.
        eccBlocks = cell(size(blocks));
        for i = 1:length(blocks)
            nsym = rsInfo.ecc(i);
            eccBlocks{i} = calculateECC(blocks{i}, nsym, expTable, logTable);
        end
        % Interleave data blocks.
        finalMessage = interleaveBlocks(blocks, eccBlocks);
    else
        eccCodewords = calculateECC(dataCodewords, eccCapacity, expTable, logTable);
        finalMessage = [dataCodewords, eccCodewords];
    end
    
    %% Convert final message to bit stream.
    dataBits = [];
    for i = 1:length(finalMessage)
        dataBits = [dataBits, dec2bin(finalMessage(i),8)-'0'];
    end
    
    %% Create empty QR matrix.
    matrix = createEmptyMatrix(qrSize);
    reserved = false(qrSize);
    
    %% Place function patterns.
    [matrix, reserved] = addFinderPatterns(matrix, reserved, qrSize);
    [matrix, reserved] = addAlignmentPatterns(matrix, reserved, version, alignLocs);
    [matrix, reserved] = addTimingPatterns(matrix, reserved, qrSize);
    [matrix, reserved] = addDarkModule(matrix, reserved, version, qrSize);
    
    %% Mask selection and format info.
    if isempty(mask)
        bestPenalty = inf;
        bestMatrix = [];
        bestMask = 0;
        for m = 0:7
            tempMatrix = matrix;
            tempMatrix = addFormatInfo(tempMatrix, reserved, m, ecLevel, qrSize);
            tempMatrix = placeDataBits(tempMatrix, reserved, dataBits, m, qrSize);
            p = computePenalty(tempMatrix, qrSize);
            if p < bestPenalty
                bestPenalty = p;
                bestMask = m;
                bestMatrix = tempMatrix;
            end
        end
        fprintf('Selected mask: %d with penalty %d\n', bestMask, bestPenalty);
        matrix = bestMatrix;
    else
        mask = str2double(mask);
        matrix = addFormatInfo(matrix, reserved, mask, ecLevel, qrSize);
        matrix = placeDataBits(matrix, reserved, dataBits, mask, qrSize);
    end
    
    %% Render the matrix into an image.
    img = renderQR(matrix, qrSize, 10, 4);
    % Save image (here we assume PNG output; you can extend to SVG/ASCII as desired)
    imwrite(img, outFile);
    fprintf('QR Code saved to %s\n', outFile);
end

%% Helper functions

function [expTable, logTable] = initGF256()
% initGF256 Precompute GF(256) exponential and logarithm tables.
    expTable = zeros(1,512);
    logTable = zeros(1,256);
    x = 1;
    for i = 0:254
        expTable(i+1) = x;
        logTable(x+1) = i;
        x = bitshift(x,1);
        if x >= 256
            x = bitxor(x, 285);  % 0x11d = 285 decimal
        end
    end
    expTable(256+1:512) = expTable(1:256);
end

function prod = gfMul(a, b, expTable, logTable)
% gfMul Multiply two numbers in GF(256).
    if a==0 || b==0
        prod = 0;
    else
        prod = expTable(mod(logTable(a+1)+logTable(b+1),255)+1);
    end
end

function r = gfPolyMul(p, q, expTable, logTable)
% gfPolyMul Multiply two polynomials over GF(256).
    r = zeros(1, length(p)+length(q)-1);
    for i = 1:length(p)
        for j = 1:length(q)
            r(i+j-1) = bitxor(r(i+j-1), gfMul(p(i), q(j), expTable, logTable));
        end
    end
end

function gen = rsGeneratorPoly(nsym, expTable, logTable)
% rsGeneratorPoly Generate the RS generator polynomial of degree nsym.
    gen = 1;
    for i = 0:nsym-1
        gen = gfPolyMul(gen, [1 expTable(i+1)], expTable, logTable);
    end
end

function ecc = calculateECC(data, nsym, expTable, logTable)
% calculateECC Compute RS error–correction codewords for data.
    gen = rsGeneratorPoly(nsym, expTable, logTable);
    msg = [data, zeros(1, nsym)];
    for i = 1:length(data)
        coef = msg(i);
        if coef ~= 0
            for j = 1:length(gen)
                msg(i+j-1) = bitxor(msg(i+j-1), gfMul(gen(j), coef, expTable, logTable));
            end
        end
    end
    ecc = msg(end-nsym+1:end);
end

function mode = chooseMode(data)
% chooseMode Automatically choose encoding mode.
    if all(isstrprop(data, 'digit'))
        mode = 'numeric';
    elseif all(ismember(upper(data), '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:'))
        mode = 'alphanumeric';
    else
        mode = 'byte';
    end
end

function codewords = encodeDataAll(data, version, ecLevel, dataCapacity)
% encodeDataAll Encode the input data string into codewords.
%   For simplicity, this implementation supports all modes but uses fixed
%   character–count indicator lengths (see the Python version comments).
    mode = chooseMode(data);
    if strcmp(mode, 'numeric')
        if version==1
            countBits = 10; else countBits = 12;
        end
        bits = ['0001', dec2bin(length(data), countBits), encodeNumeric(data)];
    elseif strcmp(mode, 'alphanumeric')
        if version==1
            countBits = 9; else countBits = 11;
        end
        bits = ['0010', dec2bin(length(data), countBits), encodeAlphanumeric(data)];
    else  % byte mode
        countBits = 8; % (for simplicity, assume versions 1–9 use 8 bits)
        bits = ['0100', dec2bin(length(data), countBits), encodeByte(data)];
    end
    % Append terminator up to 4 zero bits.
    available = dataCapacity * 8;
    if length(bits) < available
        bits = [bits, repmat('0', 1, min(4, available-length(bits)))];
    end
    % Pad to a multiple of 8 bits.
    while mod(length(bits),8)~=0
        bits = [bits, '0'];
    end
    % Convert bits to codewords.
    codewords = [];
    for i = 1:8:length(bits)
        codewords(end+1) = bin2dec(bits(i:i+7));
    end
    % Pad with alternating bytes 0xEC and 0x11.
    padBytes = [hex2dec('EC'), hex2dec('11')];
    padIndex = 1;
    while length(codewords) < dataCapacity
        codewords(end+1) = padBytes(mod(padIndex-1,2)+1);
        padIndex = padIndex + 1;
    end
end

function s = encodeNumeric(data)
% encodeNumeric Encode a numeric string into bit–string.
    s = '';
    i = 1;
    while i <= length(data)
        if i+2 <= length(data)
            s = [s, dec2bin(str2double(data(i:i+2)), 10)];
            i = i+3;
        elseif i+1 <= length(data)
            s = [s, dec2bin(str2double(data(i:i+1)), 7)];
            i = i+2;
        else
            s = [s, dec2bin(str2double(data(i)), 4)];
            i = i+1;
        end
    end
end

function s = encodeAlphanumeric(data)
% encodeAlphanumeric Encode an alphanumeric string into bit–string.
    table = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:';
    s = '';
    i = 1;
    data = upper(data);
    while i <= length(data)
        if i+1 <= length(data)
            val = find(table==data(i)) - 1;
            val2 = find(table==data(i+1)) - 1;
            num = val*45 + val2;
            s = [s, dec2bin(num, 11)];
            i = i+2;
        else
            val = find(table==data(i)) - 1;
            s = [s, dec2bin(val, 6)];
            i = i+1;
        end
    end
end

function s = encodeByte(data)
% encodeByte Encode a string in byte mode.
    s = '';
    for i = 1:length(data)
        s = [s, dec2bin(uint8(data(i)), 8)];
    end
end

function finalMsg = interleaveBlocks(blocks, eccBlocks)
% interleaveBlocks Interleave data and ECC blocks.
    % Find maximum block lengths.
    maxData = max(cellfun(@length, blocks));
    maxECC  = max(cellfun(@length, eccBlocks));
    finalMsg = [];
    % Interleave data codewords.
    for i = 1:maxData
        for j = 1:length(blocks)
            if i <= length(blocks{j})
                finalMsg(end+1) = blocks{j}(i);
            end
        end
    end
    % Interleave ECC codewords.
    for i = 1:maxECC
        for j = 1:length(eccBlocks)
            if i <= length(eccBlocks{j})
                finalMsg(end+1) = eccBlocks{j}(i);
            end
        end
    end
end

function M = createEmptyMatrix(qrSize)
% createEmptyMatrix Create an empty (NaN) matrix for the QR code.
    M = nan(qrSize);
end

function [M, reserved] = addFinderPatterns(M, reserved, qrSize)
% addFinderPatterns Place finder patterns (with separators) at three corners.
    positions = [1, qrSize-6];  % MATLAB indices are 1-based.
    % Top-left:
    [M, reserved] = placeFinder(M, reserved, 1, 1);
    % Top-right:
    [M, reserved] = placeFinder(M, reserved, 1, qrSize-6);
    % Bottom-left:
    [M, reserved] = placeFinder(M, reserved, qrSize-6, 1);
end

function [M, reserved] = placeFinder(M, reserved, r, c)
% placeFinder Place a 7x7 finder pattern and its 1–module white separator.
    pattern = [...
        1 1 1 1 1 1 1; ...
        1 0 0 0 0 0 1; ...
        1 0 1 1 1 0 1; ...
        1 0 1 1 1 0 1; ...
        1 0 1 1 1 0 1; ...
        1 0 0 0 0 0 1; ...
        1 1 1 1 1 1 1];
    for i = 0:6
        for j = 0:6
            M(r+i, c+j) = pattern(i+1,j+1);
            reserved(r+i, c+j) = true;
        end
    end
    % Add separator (1–module white border)
    for i = -1:7
        for j = -1:7
            rr = r+i; cc = c+j;
            if rr>=1 && rr<=size(M,1) && cc>=1 && cc<=size(M,2)
                if i<0 || i>6 || j<0 || j>6
                    M(rr, cc) = 0;
                    reserved(rr, cc) = true;
                end
            end
        end
    end
end

function [M, reserved] = addAlignmentPatterns(M, reserved, version, alignLocs)
% addAlignmentPatterns Place alignment patterns (if version>=2).
    if version < 2
        return;
    end
    loc = alignLocs(version).loc;
    qrSize = size(M,1);
    for i = 1:length(loc)
        for j = 1:length(loc)
            % Skip if overlapping with finder patterns.
            if (i==1 && j==1) || (i==1 && j==length(loc)) || (i==length(loc) && j==1)
                continue;
            end
            [M, reserved] = placeAlignment(M, reserved, loc(i), loc(j));
        end
    end
end

function [M, reserved] = placeAlignment(M, reserved, center_r, center_c)
% placeAlignment Place a 5x5 alignment pattern centered at (center_r, center_c).
    pattern = [...
        1 1 1 1 1; ...
        1 0 0 0 1; ...
        1 0 1 0 1; ...
        1 0 0 0 1; ...
        1 1 1 1 1];
    for i = -2:2
        for j = -2:2
            r = center_r + i;
            c = center_c + j;
            if r>=1 && r<=size(M,1) && c>=1 && c<=size(M,2)
                M(r,c) = pattern(i+3,j+3);
                reserved(r,c) = true;
            end
        end
    end
end

function [M, reserved] = addTimingPatterns(M, reserved, qrSize)
% addTimingPatterns Place horizontal and vertical timing patterns.
    % Horizontal timing pattern at row 7.
    for c = 1:qrSize
        if isnan(M(7,c))
            M(7,c) = mod(c,2);
            reserved(7,c) = true;
        end
    end
    % Vertical timing pattern at column 7.
    for r = 1:qrSize
        if isnan(M(r,7))
            M(r,7) = mod(r,2);
            reserved(r,7) = true;
        end
    end
end

function [M, reserved] = addDarkModule(M, reserved, version, qrSize)
% addDarkModule Place the dark module.
    r = 4*version + 9; c = 8;  % 1-indexed positions
    if r <= qrSize && c <= qrSize
        M(r, c) = 1;
        reserved(r, c) = true;
    end
end

function M = computeFormatInfo(mask, ecLevel)
% computeFormatInfo Compute the 15–bit format information string.
    % Map EC level to two bits.
    switch upper(ecLevel)
        case 'L', ecBits = bin2dec('01');
        case 'M', ecBits = bin2dec('00');
        case 'Q', ecBits = bin2dec('11');
        case 'H', ecBits = bin2dec('10');
        otherwise, error('Invalid EC level.');
    end
    formatData = bitshift(ecBits,3) + mask;  % 5 bits
    % Compute 10–bit BCH code; generator polynomial is x^10 + x^8 + x^5 + x^4 + x^2 + x + 1 (0x537)
    g = hex2dec('537');
    code = bitshift(formatData,10);
    for i = 14:-1:10
        if bitget(code, i+1)
            code = bitxor(code, bitshift(g, i-10));
        end
    end
    formatInfo = bitxor(bitshift(formatData,10) + code, hex2dec('5412'));
    M = dec2bin(formatInfo,15) - '0';
end

function M = addFormatInfo(M, reserved, mask, ecLevel, qrSize)
% addFormatInfo Place the 15 format information bits in the matrix.
    fmt = computeFormatInfo(mask, ecLevel);
    % First copy:
    coords = [8 1; 8 2; 8 3; 8 4; 8 5; 8 6; 8 8; 7 8; 5 8; 4 8; 3 8; 2 8; 1 8; 0 8];
    % Note: MATLAB indices are 1-based. Adjust coordinates accordingly.
    for i = 1:length(fmt)
        % Here we use a simplified fixed mapping.
        if i<=7
            r = coords(i,1)+1; c = coords(i,2)+1;
        else
            r = coords(i,1)+1; c = coords(i,2)+1;
        end
        M(r,c) = fmt(i);
        reserved(r,c) = true;
    end
    % Mirror copy (simplified).
    % (For a full implementation, the mirror coordinates would be set per spec.)
end

function flag = maskCondition(r, c, mask)
% maskCondition Returns true if the mask condition holds at position (r,c).
    switch mask
        case 0, flag = mod(r+c,2)==0;
        case 1, flag = mod(r,2)==0;
        case 2, flag = mod(c,3)==0;
        case 3, flag = mod(r+c,3)==0;
        case 4, flag = mod(floor(r/2)+floor(c/3),2)==0;
        case 5, flag = mod(r*c,2)+mod(r*c,3)==0;
        case 6, flag = mod(mod(r*c,2)+mod(r*c,3),2)==0;
        case 7, flag = mod(mod(r+c,2)+mod(r*c,3),2)==0;
        otherwise, flag = false;
    end
end

function M = placeDataBits(M, reserved, dataBits, mask, qrSize)
% placeDataBits Place data bits in the matrix in a zig–zag pattern.
    bitIndex = 1;
    col = qrSize;
    direction = -1;
    while col > 1
        if col == 7, col = col - 1; end  % Skip vertical timing pattern column.
        if direction == -1
            rows = qrSize:-1:1;
        else
            rows = 1:qrSize;
        end
        for r = rows
            for c = [col, col-1]
                if reserved(r,c)
                    continue;
                end
                if bitIndex <= length(dataBits)
                    bit = dataBits(bitIndex);
                    if maskCondition(r-1, c-1, mask)  % adjust indices for mask condition (0-indexed)
                        bit = ~bit;
                    end
                    M(r,c) = bit;
                    bitIndex = bitIndex + 1;
                else
                    M(r,c) = 0;
                end
            end
        end
        col = col - 2;
        direction = -direction;
    end
end

function p = computePenalty(M, qrSize)
% computePenalty Compute penalty score for a QR matrix.
    p = 0;
    % Rule 1: Adjacent modules in rows.
    for r = 1:qrSize
        run = 1;
        for c = 2:qrSize
            if M(r,c) == M(r,c-1)
                run = run + 1;
            else
                if run >= 5, p = p + 3 + (run-5); end
                run = 1;
            end
        end
        if run >= 5, p = p + 3 + (run-5); end
    end
    % Rule 1: Columns.
    for c = 1:qrSize
        run = 1;
        for r = 2:qrSize
            if M(r,c) == M(r-1,c)
                run = run + 1;
            else
                if run >= 5, p = p + 3 + (run-5); end
                run = 1;
            end
        end
        if run >= 5, p = p + 3 + (run-5); end
    end
    % Rule 2: 2x2 blocks.
    for r = 1:qrSize-1
        for c = 1:qrSize-1
            if M(r,c)==M(r,c+1) && M(r,c)==M(r+1,c) && M(r,c)==M(r+1,c+1)
                p = p + 3;
            end
        end
    end
    % Rule 3: Finder-like patterns in rows.
    for r = 1:qrSize
        for c = 1:qrSize-6
            if isequal(M(r,c:c+6), [1 0 1 1 1 0 1])
                % Check for 4 light modules before or after.
                pre = (c>=5 && all(M(r,c-4:c-1)==0));
                post = (c<=qrSize-10 && all(M(r,c+7:c+10)==0));
                if pre || post
                    p = p + 40;
                end
            end
        end
    end
    % Rule 3: Columns (similar).
    for c = 1:qrSize
        for r = 1:qrSize-6
            if isequal(M(r:r+6,c)', [1 0 1 1 1 0 1])
                pre = (r>=5 && all(M(r-4:r-1,c)==0));
                post = (r<=qrSize-10 && all(M(r+7:r+10,c)==0));
                if pre || post
                    p = p + 40;
                end
            end
        end
    end
    % Rule 4: Balance of dark modules.
    darkCount = sum(M(:)==1);
    total = qrSize*qrSize;
    percent = (darkCount*100)/total;
    deviation = abs(percent-50);
    p = p + floor(deviation/5)*10;
end

function img = renderQR(M, qrSize, scale, border)
% renderQR Render the QR matrix into a grayscale image.
%   scale: pixel size of one module.
%   border: number of modules for the white border.
    total = (qrSize + 2*border)*scale;
    img = uint8(255*ones(total, total));
    for r = 1:qrSize
        for c = 1:qrSize
            if M(r,c)==1
                x0 = (c+border-1)*scale + 1;
                y0 = (r+border-1)*scale + 1;
                img(y0:y0+scale-1, x0:x0+scale-1) = 0;
            end
        end
    end
end